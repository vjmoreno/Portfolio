# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.tools.translate import _
from odoo import tools
from odoo.exceptions import ValidationError, UserError
from odoo.addons.base.models.res_partner import _tz_get
from odoo.addons.addon_restful.common import rest_api_model, rest_api_method
from dateutil.relativedelta import relativedelta
import re


class EmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    name = fields.Char(required=False)
    name_full = fields.Char(required=False)
    first_name = fields.Char('First name', required=True)
    last_name = fields.Char('Last name', required=True)
    middle_name = fields.Char('Middle name')
    nickname = fields.Char('Nickname', copy=False)
    start_date = fields.Date('Start Date')
    bio = fields.Text('Bio')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('hiring', 'Hiring'),
        ('active', 'Active'),
        ('terminated', 'Terminated'),
        ('leave_of_absence', 'Leave of Absence')
    ], string='Status', default='draft')

    employee_pronoun = fields.Selection([('he', 'He / him'), ('she', 'She / her'), ('they', 'They / them')],
                                        string='Preferred pronoun')

    @api.model
    def ensure_names(self):
        employees = self.search([('name', '!=', False), '|', ('first_name', '=', False), ('last_name', '=', False)])

        for employee in employees:
            names = employee.name.split(' ')
            if names:
                first_name = names[0]
                last_name = ' '.join(names[1:])
                if not last_name:
                    last_name = 'Not Given'

                employee.write({
                    'first_name': first_name,
                    'last_name': last_name
                })
        return

    @api.model
    def _compute_full_name(self, first_name, last_name, middle_name=None, nickname=None):
        fullname = ''
        if nickname:
            fullname += f'({nickname}) '
        fullname += f'{first_name} '
        if middle_name:
            fullname += f'{middle_name} '
        fullname += f'{last_name}'
        return fullname

    def compute_full_name(self):
        for employee in self:
            employee.name_full = self._compute_full_name(employee.first_name, employee.last_name, employee.middle_name,
                                                         employee.nickname)
        return True

    @api.model
    def _compute_short_name(self, first_name, last_name, nickname=None):
        fullname = ''
        if nickname:
            fullname += f'({nickname}) '
        fullname += f'{first_name} '
        if last_name:
            fullname += f'{last_name} '
        return fullname

    def compute_short_name(self):
        for employee in self:
            employee.name = self._compute_short_name(employee.first_name, employee.last_name, employee.nickname)

        return True

    @api.model
    def create(self, vals):
        vals['name_full'] = self._compute_full_name(vals['first_name'], vals['last_name'], vals.get('middle_name'),
                                                    vals.get('nickname'))
        vals['name'] = self._compute_short_name(vals['first_name'], vals['last_name'], vals.get('nickname'))
        return super(EmployeeBase, self).create(vals)

    def write(self, vals):
        res = super(EmployeeBase, self).write(vals)

        employee_image = None
        if 'image_1920' in vals:
            employee_image = vals.pop('image_1920')
            if self.env.context.get('ignore_image'):
                employee_image = None

        if vals.get('nickname') is not None or vals.get('first_name') is not None or \
                vals.get('last_name') is not None or vals.get('middle_name') is not None:
            for employee in self:
                employee.name_full = self._compute_full_name(employee.first_name, employee.last_name,
                                                             employee.middle_name, employee.nickname)
                employee.name = self._compute_short_name(employee.first_name, employee.last_name, employee.nickname)

        if employee_image is not None:
            self.mapped('user_id').with_context(ignore_image=True).write({'image_1920': employee_image})

        return res


@rest_api_model
class Employee(models.Model):
    _inherit = 'hr.employee'

    company_id = fields.Many2one(required=True)
    bio = fields.Text('Bio')
    fully_vaccinated = fields.Boolean(default=False)
    new_work_email = fields.Char('New Work Email')
    seat_preference = fields.Selection([('doesnt_matter', 'Does not matter'),
                                        ('aisle', 'Aisle'),
                                        ('middle', 'Middle'),
                                        ('window', 'Window'),
                                        ('emergency_exit', 'Emergency Exit')], default='doesnt_matter')
    pre_check_tsa = fields.Char(string='pre check TSA')
    work_location_id = fields.Many2one(
        'hr.employee.work.location', string='Work location'
    )
    # Deprecated
    home_work_location_id = fields.Many2one(
        'hr.employee.work.location', string='Home Work location'
    )
    work_location_tz = fields.Selection(
        selection=_tz_get,
        string='Timezone',
        compute='_get_work_location_tz',
        store=False
    )
    dietary_restriction_ids = fields.Many2many('hr.employee.dietary.restriction', 'hr_employee_dietary_restriction_rel', 'employee_id',
                                               'dietary_restriction_id', 'Dietary Restrictions')

    def _default_language(self):
        english = self.env['hr.language'].search([('name', '=', 'English')])
        return [[4, english[0].id]] or False

    language_ids = fields.Many2many('hr.language', 'hr_employee_language_group_rel', 'employee_id', 'language_id',
                                    'Languages', default=_default_language)
    tshirt_size = fields.Many2one('hr.tshirt.size', string='T-Shirt size')

    x_css = fields.Html(string='CSS', sanitize=False, compute='_compute_css', store=False)
    is_remote = fields.Boolean("Work from home", default=False)
    citizenships_ids = fields.Many2many('res.country', 'res_country_hr_employee_real',
                                        'employee_id', 'country_id', 'Citizenships')
    unavailable_msg = fields.Char('Unavailability message')
    unavailable_msg_tomorrow = fields.Char('Unavailability message (tomorrow)')
    country_work_location = fields.Many2one('res.country', string='Country of the Work location',
                                            compute='_get_work_location_data', store=True)
    state_work_location = fields.Many2one('res.country.state', string='State of the Work location',
                                            compute='_get_work_location_data', store=True)
    work_location_text = fields.Char(compute='_get_work_location_data')
    health_document_ids = fields.One2many('hr.employee.health', 'employee_id')
    citizenship_document_ids = fields.One2many('hr.employee.citizenship', 'employee_id')
    travel_document_ids = fields.One2many('hr.employee.travel', 'employee_id')
    frequent_flyer_ids = fields.One2many('hr.employee.frequent.flyer', 'employee_id')
    travel_special_assistance_ids = fields.Many2many('travel.special.assistance', 'hr_employee_special_assistance', 'employee_id',
                                                     'travel_special_assistance_id', 'Special Assistance')
    gender = fields.Selection(selection_add=[('other', 'Non-Binary')])
    employment_period_ids = fields.One2many('employment.period', 'employee_id', 'Employment Periods')

    @api.model
    def default_get(self, fields_list):
        res = super(Employee, self).default_get(fields_list)
        if not res.get('dietary_restriction_ids') and 'dietary_restriction_ids' not in res:
            res.update({'dietary_restriction_ids': [(6, 0, self.env.ref('addon_hr_customizations.hr_employee_dietary_restriction_none',
                                                                        raise_if_not_found=False).ids)]})
        if not res.get('travel_special_assistance_ids') and 'travel_special_assistance_ids' not in res:
            res.update({'travel_special_assistance_ids': [(6, 0, self.env.ref('addon_hr_customizations.travel_special_assistance_none',
                                                                              raise_if_not_found=False).ids)]})
        return res

    @api.constrains('work_email')
    def check_email_duplicates(self):
        for rec in self:
            if self.search([('work_email', '=', rec.work_email), ('id', '!=', rec.id), ('work_email', '!=', False)]):
                raise UserError('Employee with same work email already exists!')

    @api.constrains('frequent_flyer_ids')
    def check_frequent_flyer_ids(self):
        for record in self:
            program_ids = [program_id.loyalty_program_id.id for program_id in record.frequent_flyer_ids]
            if record.frequent_flyer_ids and len(program_ids) != len(set(program_ids)):
                raise UserError("You cannot have the same loyalty program twice in the same employee.")

    def _register_hook(self):
        columns = tools.table_columns(self._cr, self._table)
        if 'first_name' not in columns:
            tools.create_column(self._cr, self._table, 'first_name', 'VARCHAR')
        if 'last_name' not in columns:
            tools.create_column(self._cr, self._table, 'last_name', 'VARCHAR')
        if 'middle_name' not in columns:
            tools.create_column(self._cr, self._table, 'middle_name', 'VARCHAR')
        if 'nickname' not in columns:
            tools.create_column(self._cr, self._table, 'nickname', 'VARCHAR')
        if 'work_location_text' not in columns:
            tools.create_column(self._cr, self._table, 'work_location_text', 'VARCHAR')
        if 'start_date' not in columns:
            tools.create_column(self._cr, self._table, 'start_date', 'DATE')
        if 'bio' not in columns:
            tools.create_column(self._cr, self._table, 'bio', 'TEXT')
        if 'new_work_email' not in columns:
            tools.create_column(self._cr, self._table, 'new_work_email', 'VARCHAR')
        if 'fully_vaccinated' not in columns:
            tools.create_column(self._cr, self._table, 'fully_vaccinated', 'BOOLEAN')
        if 'pre_check_tsa' not in columns:
            tools.create_column(self._cr, self._table, 'pre_check_tsa', 'VARCHAR')
        if 'seat_preference' not in columns:
            tools.create_column(self._cr, self._table, 'seat_preference', 'VARCHAR')

        return super(Employee, self)._register_hook()

    @api.depends('state')
    def _compute_css(self):
        """ hide archive and delete actions depend on state """
        for employee in self:
            if employee.state in ['draft', 'hiring']:
                employee.x_css = '<style>.o_sidebar_item_archive {display: none !important;}</style>'

            elif employee.state in ['terminated']:
                employee.x_css = '<style>.undefined {display: none !important;}</style>'

            elif employee.state in ['active', 'leave_of_absence']:
                employee.x_css = '<style>.o_dropdown {display: none !important;}</style>'

            else:
                employee.x_css = False

    def button_force_state(self):
        action = self.env.ref("addon_hr_customizations.force_employee_transition_action").read()[0]
        action['context'] = {'default_employee_id': self.id}
        return action

    def button_hiring(self):
        action = self.env.ref("addon_hr_customizations.create_employee_action").read()[0]
        action['context'] = {'default_employee_id': self.id}
        return action

    def button_activate(self):
        action = self.env.ref("addon_hr_customizations.activate_employee_action").read()[0]
        action['context'] = {'default_employee_id': self.id}
        return action

    def button_terminate(self):
        if not self.parent_id or (self.parent_id.state != 'active'):
            raise UserError('Cannot transition because Employee does no active supervisor')
        else:
            return {
                'name': "%s Activities" % self.name_full,
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.employee.activities.wizard',
                'context': {'default_employee_id': self.id, 'default_supervisor_id': self.parent_id.id,
                            'default_clicked_button': 'terminate'},
                'view_id': self.env.ref('addon_hr_customizations.employee_activities_wizard_view_form').id,
                'target': 'new'
            }

    def button_rehire(self):
        self.state = 'draft'

    def button_leave_of(self):
        if not self.parent_id or (self.parent_id.state != 'active'):
            raise UserError('Cannot transition because Employee does no active supervisor')
        else:
            return {
                'name': "%s Activities" % self.name_full,
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.employee.activities.wizard',
                'context': {'default_employee_id': self.id, 'default_supervisor_id': self.parent_id.id,
                            'default_clicked_button': 'leave'},
                'view_id': self.env.ref('addon_hr_customizations.employee_activities_wizard_view_form').id,
                'target': 'new'
            }

    @api.model
    def set_availability(self):
        self.search([('work_location_id', '=', False)]).write({
            'unavailable_msg': False,
            'unavailable_msg_tomorrow': False
        })

        today = fields.Date.today()
        tomorrow = today + relativedelta(days=1)
        holidays_obj = self.env['holidays.holiday']

        for employee in self.search([('work_location_id', '!=', False)]):
            employee.unavailable_msg = holidays_obj.get_unavailability_message(employee.id, today)
            employee.unavailable_msg_tomorrow = holidays_obj.get_unavailability_message(employee.id, tomorrow)

        return True

    @api.onchange('is_remote')
    def onchange_is_remote(self):
        """ We save home location so we don't have to create a new home work location
            every time we go from wfh to not-wfh and back again to wfh.
        """
        if self.is_remote and not self.address_home_id and self.state is not 'draft':
            raise ValidationError('Enter employee home address!')

        if self.is_remote and self.state is not 'draft' and (not self.address_home_id.city or not self.address_home_id.country_id):
            raise ValidationError('Enter employee full home address!')

        if self.is_remote:
            self.work_location_id = False

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Employee, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                    submenu=submenu)
        employees = self.env['hr.employee'].search([])
        english = self.env['hr.language'].search([('name', '=', 'English')])
        if english:
            for line in employees.filtered(lambda x: english[0].id not in x.language_ids.ids):
                line.language_ids = [[4, english[0].id]]
        for rec in employees:
            for line in rec.language_ids:
                if len(self.env['hr.language.line'].search(
                        [('employee_id', '=', rec.id), ('language_id', '=', line.id)])) < 1:
                    self.env['hr.language.line'].create({
                        'employee_id': rec.id,
                        'language_id': line.id
                    })
        return res

    def update_user_tz_based_on_work_location(self):
        for employee in self:
            if employee.work_location_tz and employee.user_id:
                employee.user_id.tz = employee.work_location_tz
        return True

    @api.model
    def create(self, vals):
        employee = super(Employee, self.with_context(is_create=True)).create(vals)
        employee.update_user_tz_based_on_work_location()
        for line in employee.language_ids:
            self.env['hr.language.line'].create({
                'employee_id': employee.id,
                'language_id': line.id
            })
        return employee

    def write(self, vals):
        res = super(Employee, self).write(vals)
        if vals.get('work_location_id'):
            self.update_user_tz_based_on_work_location()
        lang_ids = []
        if vals.get('language_ids'):
            for line in self.language_ids:
                if len(self.env['hr.language.line'].search(
                        [('employee_id', '=', self.id), ('language_id', '=', line.id)])) < 1:
                    self.env['hr.language.line'].create({
                        'employee_id': self.id,
                        'language_id': line.id
                    })
                lang_ids.append(line.id)
            deleted_lang = self.env['hr.language.line'].search(
                [('employee_id', '=', self.id), ('language_id.id', 'not in', lang_ids)])
            if len(deleted_lang) > 0:
                for line in deleted_lang:
                    line.unlink()
        return res

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'hiring'):
                raise UserError(_('Sorry, you can only delete employee in state Draft or Hiring.'))
            return super(Employee, rec).unlink()

    @api.depends('work_location_id', 'work_location_id.tz', 'address_home_id', 'address_home_id.tz', 'is_remote')
    def _get_work_location_tz(self):
        for rec in self:
            if rec.is_remote and rec.address_home_id:
                rec.work_location_tz = rec.address_home_id.tz
            elif not rec.is_remote and rec.work_location_id:
                rec.work_location_tz = rec.work_location_id.tz
            else:
                rec.work_location_tz = False

    # ---------------------------------------------------------
    # Messaging
    # ---------------------------------------------------------
    def _message_log(self, **kwargs):
        if self.env.context.get('is_create', False):
            return True
        return super(Employee, self._post_author())._message_log(**kwargs)

    # ----------------------------------------------------
    # Rest API Methods
    # ----------------------------------------------------
    @rest_api_method()
    @api.model
    def employee_work_location_id(self, employee_id):
        employee = self.browse(employee_id)
        return employee and employee.work_location_id and employee.work_location_id.id or False

    @api.depends('work_location_id', 'work_location_id.country_id', 'work_location_id.state_id',
                 'address_home_id', 'address_home_id.country_id', 'address_home_id.state_id', 'is_remote')
    def _get_work_location_data(self):
        for rec in self:
            record = rec.work_location_id if not rec.is_remote else rec.address_home_id
            rec.work_location_text = f'{record.city}, {record.state_id.display_name if record.state_id and record.state_id.name != "Blank" else record.country_id.name}' if record else ''
            rec.country_work_location = record.country_id.id
            rec.state_work_location = record.state_id.id

    @rest_api_method()
    @api.model
    def employee_work_location_is_home(self, employee_id):
        employee = self.browse(employee_id)
        return employee.is_remote

    def work_location_is_home(self):
        self.ensure_one()
        return self.employee_work_location_is_home(self.id)

    @rest_api_method()
    @api.model
    def get_employee_info(self, user_id=False, employee_id=False):
        self = self.sudo()
        fields = self.env['hr.employee']._fields.keys()

        if employee_id:
            return self.browse(employee_id).read(fields)[0]
        if user_id:
            employee = self.search([('user_id', '=', user_id)], limit=1)
            return employee and employee.read(fields)[0] or {}

        employee = self.search([('user_id', '=', self.env.user.id)], limit=1)
        return employee and employee.read(fields)[0] or {}

    def create_odoo_work_user(self):
        self.ensure_one()
        self.create_work_user_preconditions()
        partner_id = self.env['res.partner'].search([('email', '=', self.work_email)], limit=1)
        user_id = self.env['res.users'].search([('login', '=', self.work_email)], limit=1)
        if user_id:
            self.user_id = user_id.id
            self.message_post(body=f'Existing user with email {self.work_email} is linked to employee')
        else:
            user_id = self.env['res.users'].with_context(no_reset_password=True).create({
                'name': self.name,
                'login': self.work_email,
                'email': self.work_email,
                'partner_id': partner_id and partner_id.id or False,
                'groups_id': [(4, self.env.ref('base.group_user').id)],
                'image_1920': self.image_1920 or partner_id.image_1920
            })
            self.user_id = user_id
            self.message_post(body=f'Work user with email {self.work_email} is created')
        try:
            user_id.with_context(create_user=True).action_reset_password()
        except:
            self.message_post(body=f'Invite for <b>{self.work_email}</b> failed to send')

    def create_work_user_preconditions(self):
        if not self.work_email:
            raise UserError(_('This user does not have a work email. Please add it!'))
        if not self.check_email_valid(self.work_email):
            raise UserError(_(f'Email address {self.work_email} is not valid!'))
        email_domain = self.work_email[self.work_email.find('@')+1:]
        company_email_domains = self.env['nanoramic.email.domain'].get_domain_set()
        if company_email_domains and email_domain not in company_email_domains:
            raise UserError(_(f'Email domain @{email_domain} is not allowed!'))

    def deactiveate_work_user(self):
        if self.user_id:
            self.user_id.active = False
            self.message_post(body=f'Work user account with email <b>{self.work_email}</b> is disabled')

    def activate_work_user(self):
        if self.user_id and not self.user_id.active:
            self.user_id.active = True
            self.message_post(body=f'Work user account with email <b>{self.work_email}</b> is active')
            try:
                self.user_id.with_context(create_user=True).action_reset_password()
            except:
                self.message_post(body=f'Invite for <b>{self.work_email}</b> failed to send')

    def check_email_valid(self, email):
        e_index = email.find("@")
        if e_index < 0:
            return False
        user_part, domain_part = email.rsplit('@', 1)
        user_regex = re.compile(
            r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"  # dot-atom
            r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',
            # quoted-string
            re.IGNORECASE
        )
        domain_regex = re.compile(
            # max length for domain name labels is 63 characters per RFC 1034
            r'((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+)(?:[A-Z0-9-]{2,63}(?<!-))\Z',
            re.IGNORECASE
        )
        return user_regex.match(user_part) and domain_regex.match(domain_part)

    def action_change_work_email(self):
        view_id = self.env.ref('addon_hr_customizations.employee_change_work_email').id
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': view_id,
            'views': [[view_id, 'form']],
            'target': 'new',
        }

    def button_change_work_email(self):
        if not self.check_email_valid(self.new_work_email):
            raise UserError(_(f'Email address {self.new_work_email} is not valid!'))
        boardings = self.env['onboarding.record'].search([('work_email', '=', self.work_email)])
        if boardings:
            boardings.write({
                'work_email': self.new_work_email
            })
            for rec in boardings:
                rec.message_post(
                    body=f'Work email changed from <b>{self.work_email}</b> to <b>{self.new_work_email}</b>')

        partners = self.env['res.partner'].search([('email', '=', self.work_email)])
        if partners:
            partners.write({
                'email': self.new_work_email
            })
            for rec in partners:
                rec.message_post(body=f'Email changed from <b>{self.work_email}</b> to <b>{self.new_work_email}</b>')

        users = self.env['res.users'].search([('email', '=', self.work_email)])
        if users:
            users.write({
                'email': self.new_work_email
            })
            for rec in users:
                rec.message_post(body=f'Email changed from <b>{self.work_email}</b> to <b>{self.new_work_email}</b>')
        self.message_post(body=f'Work email changed from <b>{self.work_email}</b> to <b>{self.new_work_email}</b>')
        self.write({
            'work_email': self.new_work_email
        })

    def add_travel_document(self):
        view_id = self.env.ref('addon_hr_customizations.hr_employee_travel_documents_form_view_wizard').id

        return{
            'type': 'ir.actions.act_window',
            'name': 'Add Travel Document',
            'res_model': 'hr.employee.travel',
            'view_mode': 'form',
            'views': [[view_id, 'form']],
            'context': {'default_employee_id': self.id},
            'target': 'new'
        }

    def add_citizenship_document(self):
        view_id = self.env.ref('addon_hr_customizations.hr_employee_citizenship_documents_form_view_wizard').id

        return{
            'type': 'ir.actions.act_window',
            'name': 'Add Citizenship Document',
            'res_model': 'hr.employee.citizenship',
            'view_mode': 'form',
            'views': [[view_id, 'form']],
            'context': {'default_employee_id': self.id},
            'target': 'new'
        }

    def add_health_document(self):
        view_id = self.env.ref('addon_hr_customizations.hr_employee_health_documents_form_view_wizard').id

        return{
            'type': 'ir.actions.act_window',
            'name': 'Add Health Document',
            'res_model': 'hr.employee.health',
            'view_mode': 'form',
            'views': [[view_id, 'form']],
            'context': {'default_employee_id': self.id},
            'target': 'new'
        }
