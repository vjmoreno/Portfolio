from odoo import api, fields, models
from odoo.exceptions import UserError

class EmployeeCreateWizard(models.TransientModel):
    _name = 'hr.employee.create.wizard'
    _description = 'Create Employee Wizard'
    _rec_name = 'full_name'

    @api.model
    def _get_default_relationships(self):
        relationships_obj = self.env.get('hr.employee.relationships')
        if relationships_obj:
            return relationships_obj.search([('name', '=', 'US Employee W2')]).id
        return False

    wizard_step = fields.Integer(default=1)
    full_name = fields.Char(compute='_compute_full_name',string='Full Name')
    first_name = fields.Char('First Name')
    last_name = fields.Char('Last Name')
    job_title = fields.Char('Job Title')
    department_id = fields.Many2one('hr.department', 'Department')
    company_id = fields.Many2one('res.company','Company')
    relationships = fields.Many2one('hr.employee.relationships', default=_get_default_relationships, string='Relationship')
    parent_id = fields.Many2one('hr.employee','Manager')
    personal_email = fields.Char(string="Personal Email")
    country_id = fields.Many2one('res.country', 'Home Country', force_save=True)
    city = fields.Char('Home City', force_save=True)
    work_location = fields.Selection([('on_site','On Site'),('from_home','From Home')], 'Work Location')
    on_site_location_id = fields.Many2one('hr.employee.work.location','On Site Location')
    contact_id = fields.Many2one('res.partner', 'Existing Personal Contact')
    birthday = fields.Date()
    start_date = fields.Date()
    employee_id = fields.Many2one('hr.employee')
    action = fields.Selection([('create', 'Create'), ('hiring', 'Hiring')], default='create')
    step_count = fields.Integer()

    @api.model
    def default_get(self, fields):
        res = super(EmployeeCreateWizard, self).default_get(fields)
        res['step_count'] = 3
        employee_id = self._context and self._context.get('default_employee_id', False)
        if employee_id:
            employee_id = self.env['hr.employee'].browse([employee_id])
            res['first_name'] = employee_id.first_name
            res['last_name'] = employee_id.last_name
            res['job_title'] = employee_id.job_title
            res['department_id'] = employee_id.department_id.id if employee_id.department_id else None
            res['company_id'] = employee_id.company_id.id if employee_id.company_id else None
            res['relationships'] = employee_id.relationships.id if employee_id.relationships else None
            res['parent_id'] = employee_id.parent_id.id if employee_id.parent_id else None
            res['personal_email'] = employee_id.private_email
            res['contact_id'] = employee_id.address_home_id.id if employee_id.address_home_id else None
            res['country_id'] = employee_id.address_home_id.country_id.id if employee_id.address_home_id.country_id else None
            res['city'] = employee_id.address_home_id.city if employee_id.address_home_id.city else None
            res['work_location'] = 'from_home' if employee_id.is_remote else 'on_site'
            res['on_site_location_id'] = employee_id.work_location_id.id if employee_id.work_location_id and not employee_id.is_remote else None
            res['employee_id'] = employee_id.id
            res['start_date'] = employee_id.start_date
            res['birthday'] = employee_id.birthday
            res['action'] = 'hiring'
            res['step_count'] = 4
        return res

    @api.onchange('personal_email')
    def _onchange_personal_email(self):
        if self.personal_email:
            contact_id = self.env['res.partner'].search([('email', '=', self.personal_email)], limit=1)
            if contact_id:
                self.contact_id = contact_id.id
                self.country_id = contact_id.country_id and contact_id.country_id.id
                self.city = contact_id.city
            else:
                self.contact_id = None

    def _compute_full_name(self):
        for rec in self:
            rec.full_name = f'{rec.first_name} {rec.last_name}'

    def next_step(self):
        if self.wizard_step == 2:
            self._check_step_2()
        elif self.wizard_step == 3:
            self._check_step_3()
        self.wizard_step += 1
        return self.action_edit()

    def _check_step_2(self):
        empty_fields = []
        if not all([self.department_id, self.company_id,self.relationships, self.parent_id]):
            if not self.department_id: empty_fields.append('Department')
            if not self.company_id: empty_fields.append('Company')
            if not self.relationships: empty_fields.append('Relationship')
            if not self.parent_id: empty_fields.append('Manager')
        if self.employee_id and not self.start_date:
            empty_fields.append('Start Date')
        if self.employee_id and not self.birthday:
            empty_fields.append('Birthday')
        if empty_fields:
            raise UserError(f'The following fields are invalid: \n {",".join(empty_fields)} ')
        return True

    def _check_step_3(self):
        empty_fields = []
        if not all([self.personal_email, self.country_id,self.city,self.work_location, self.on_site_location_id]):
            if not self.personal_email: empty_fields.append('Personal Email')
            if not self.country_id: empty_fields.append('Home Country')
            if not self.city: empty_fields.append('Home City')
            if not self.work_location or (self.work_location == 'on_site' and not self.on_site_location_id): empty_fields.append('Work Location')
            if empty_fields:
                raise UserError(f'The following fields are invalid: \n {", ".join(empty_fields)} ')
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

    def create_personal_contact(self):
        contact_id = self.contact_id if self.action == 'create' else self.employee_id.address_home_id
        contact_data = {
                'name': self.full_name,
                'function': self.job_title,
                'email': self.personal_email,
                'company_id': self.company_id.id,
                'company_type': 'person',
                'country_id': self.country_id.id,
                'city': self.city
            }
        if not contact_id:
            contact_id = self.env['res.partner'].create(contact_data)
        else:
            contact_id.write(contact_data)
        return contact_id

    def create_employee(self):
        self._check_step_3()
        contact_id = self.create_personal_contact()
        data = {
                'first_name': self.first_name,
                'last_name': self.last_name,
                'job_title': self.job_title,
                'company_id': self.company_id.id,
                'department_id': self.department_id.id,
                'parent_id': self.parent_id.id,
                'private_email': self.personal_email,
                'address_home_id': contact_id.id,
                'relationships': self.relationships.id,
                'work_location_id': self.on_site_location_id and self.on_site_location_id.id or False,
                'is_remote': True if self.work_location == 'from_home' else False,
            }
        if self.action == 'hiring':
            data = {**data, **{'state': 'hiring', 'start_date': self.start_date, 'birthday': self.birthday}}
            self.employee_id.write(data)
        else:
            employee_id = self.sudo().env['hr.employee'].create(data)

            ctx = dict(self.env.context or {})
            ctx["custom_breadcrums"] = (ctx.get("custom_breadcrums") or [])+[{"breadcrumbs": {
                'custom_breadcrum': True,
                'title': 'Employees',
                'type': 'ir.actions.act_window',
                'view_mode': 'kanban,tree,form',
                'views': [[False, 'kanban'], [False, 'list'], [False, 'form']],
                'res_model': 'hr.employee',
            }, "index": 1}]
            ctx["clear_last_breadcrum_item"] = False
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.employee',
                'res_id': employee_id.id,
                'target': 'main',
                'context': ctx,
            }
