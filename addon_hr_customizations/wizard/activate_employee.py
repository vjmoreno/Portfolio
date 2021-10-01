from datetime import date
from odoo import api, fields, models
from odoo.exceptions import UserError


class EmployeeActivateWizard(models.TransientModel):
    _name = 'hr.employee.activate.wizard'
    _description = 'Activate Employee Wizard'
    _rec_name = 'full_name'

    @api.model
    def _get_default_relationships(self):
        relationships_obj = self.env.get('hr.employee.relationships')
        if relationships_obj:
            return relationships_obj.search([('name', '=', 'US Employee W2')]).id
        return False

    wizard_step = fields.Integer(default=1)
    employee_id = fields.Many2one('hr.employee')
    full_name = fields.Char(string='Full Name')
    mail = fields.Char()
    nanoramic_mail_domain = fields.Many2one('nanoramic.email.domain', string='Email Domain', required=True)
    date_start = fields.Date()
    private_email = fields.Char(related='employee_id.private_email')
    mail_template = fields.Char(compute='_compute_mail_template', store=True, readonly=False)
    skip_mail = fields.Boolean(string='Skip Email')
    department_id = fields.Many2one('hr.department', 'Department')
    company_id = fields.Many2one('res.company', 'Company')
    birthday = fields.Date()
    relationships = fields.Many2one('hr.employee.relationships', default=_get_default_relationships,
                                    string='Relationship')
    parent_id = fields.Many2one('hr.employee', 'Manager')

    @api.model
    def default_get(self, fields):
        res = super(EmployeeActivateWizard, self).default_get(fields)
        employee_id = self._context and self._context.get('default_employee_id', False)
        if employee_id:
            employee_id = self.env['hr.employee'].browse([employee_id])
            res['full_name'] = f'{employee_id.first_name} {employee_id.last_name}'

            work_email = employee_id.work_email.split('@')[0] if employee_id.work_email else None
            res['mail'] = work_email if work_email else f'{employee_id.first_name}.{employee_id.last_name}'.lower()

            Domain = self.env['nanoramic.email.domain']
            current_domain = employee_id.work_email.split('@')[1] if employee_id.work_email else None
            current_domain = Domain.search([('name', '=', current_domain)]) if current_domain else None
            default_domain = Domain.get_default()
            default_domain = default_domain if default_domain else None
            res['nanoramic_mail_domain'] = current_domain.id if current_domain else default_domain.id if default_domain else None

            res['date_start'] = employee_id.start_date
            res['department_id'] = employee_id.department_id.id if employee_id.department_id else None
            res['company_id'] = employee_id.company_id.id if employee_id.company_id else None
            res['relationships'] = employee_id.relationships.id if employee_id.relationships else None
            res['parent_id'] = employee_id.parent_id.id if employee_id.parent_id else None
            res['birthday'] = employee_id.birthday if employee_id.birthday else None
        return res

    @api.depends('mail', 'nanoramic_mail_domain')
    def _compute_mail_template(self):
        Template = self.env['mail.template']
        template = self.env['ir.model.data'].xmlid_to_object('addon_hr_customizations.mail_template_activate_employee')
        for record in self:
            if template:
                template_id = template.get_email_template(record.employee_id.id)
                record.mail_template = Template.with_context({'new_work_email': f'{record.mail}@{record.nanoramic_mail_domain.name}'}).\
                    _render_template(template_id.body_html, 'hr.employee', record.employee_id.id)
            else:
                record.mail_template = ''

    def next_step(self):
        if self.wizard_step == 2:
            self._check_step_2()
        elif self.wizard_step == 3:
            self._check_step_3()
        elif self.wizard_step == 4:
            self._check_step_4()
        self.wizard_step += 1
        return self.action_edit()

    def _check_step_2(self):
        empty_fields = []
        if not all([self.department_id, self.company_id, self.relationships, self.parent_id, self.birthday]):
            if not self.department_id: empty_fields.append('Department')
            if not self.company_id: empty_fields.append('Company')
            if not self.relationships: empty_fields.append('Relationship')
            if not self.parent_id: empty_fields.append('Manager')
            if not self.birthday: empty_fields.append('Birthday')
        if empty_fields:
            raise UserError(f'The following fields are invalid: \n {",".join(empty_fields)} ')
        return True

    def _check_step_3(self):
        if not self.date_start:
            raise UserError(f'Please add a valid date start')
        return True

    def _check_step_4(self):
        if not self.mail or not self.nanoramic_mail_domain:
            raise UserError(f'Please add a valid mail address')
        return True

    def _check_step_5(self):
        if not self.skip_mail and not self.mail_template:
            raise UserError(f"You can't send an empty email")
        return True

    def back_step(self):
        self.wizard_step -= 1
        return self.action_edit()

    def action_edit(self):
        ctx = dict(self.env.context or {})
        return {
            'view_mode': 'form',
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': ctx,
            'res_id': self and self.ids[0] or False,
        }

    def create_work_contact(self):
        contact_id = self.env['res.partner'].search([('email', '=', self.employee_id.work_email)], limit=1)
        data = {
            'name': self.full_name,
            'function': self.employee_id.job_title,
            'company_id': self.employee_id.company_id.id,
            'company_type': 'person',
            'street': self.employee_id.address_home_id.street,
            'street2': self.employee_id.address_home_id.street2,
            'country_id': self.employee_id.address_home_id.country_id.id,
            'state_id': self.employee_id.address_home_id.state_id.id,
            'zip': self.employee_id.address_home_id.zip,
            'city': self.employee_id.address_home_id.city
        }
        if not contact_id:
            self.env['res.partner'].create({**data, **{'email': self.employee_id.work_email}})
        else:
            contact_id.write(data)

    def activate_employee(self):
        self._check_step_5()
        private_email = self.employee_id.private_email
        self.employee_id.work_email = f'{self.mail}@{self.nanoramic_mail_domain.name}'
        if not self.employee_id.user_id:
            self.employee_id.create_odoo_work_user()
        self.employee_id.activate_work_user()
        self.create_work_contact()
        self.employee_id.write({'state': 'active',
                                'start_date': self.date_start,
                                'company_id': self.company_id.id,
                                'department_id': self.department_id.id,
                                'parent_id': self.parent_id.id,
                                'relationships': self.relationships.id,
                                'birthday': self.birthday
                                })

        if not self.skip_mail:
            Template = self.env['mail.template']
            template = self.env['ir.model.data'].xmlid_to_object(
                'addon_hr_customizations.mail_template_activate_employee')
            template_id = template.get_email_template(self.employee_id.id)
            if template_id:
                subject = Template._render_template(template_id.subject, 'hr.employee', self.employee_id.id)
                emails_from = Template._render_template(template_id.email_from, 'hr.employee', self.employee_id.id)
            else:
                subject = ''
                emails_from = ''

            email = self.env['mail.mail'].create({
                'notification': True,
                'message_type': 'email',
                'subject': subject,
                'body_html': self.mail_template,
                'body': self.mail_template,
                'email_from': emails_from,
                'email_to': private_email,
                'model': 'hr.employee',
                'res_id': self.employee_id.id,
                'recipient_ids': [(self.employee_id.address_home_id.id)]
            })
            email.send()
