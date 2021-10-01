from odoo import fields, models


class HolidaysHoliday(models.Model):
    _inherit = "holidays.holiday"

    affected_employees = fields.Many2many('hr.employee', string='Affected employees', compute='compute_affected_employees')
    affected_employees_count = fields.Integer(string='Affected employees count', compute='compute_affected_employees')
    affected_employees_count_str = fields.Char(string='Affected employees count', compute='compute_affected_employees')

    def see_affected_employees(self):
        return {
            'name': 'Affected employees',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'hr.employee',
            'domain': [('id', 'in', self.affected_employees.ids)],
            'target': 'current'
        }

    def compute_affected_employees(self):
        empty_employee_recordset = self.env['hr.employee']
        for holiday in self:
            domain = [('country_id', '=', holiday.country_name.id)]
            if holiday.state_name:
                domain.append(('state_id', '=', holiday.state_name.id))
            work_locations = self.env['hr.employee.work.location'].search(domain)

            if holiday.is_public:
                affected_employees = work_locations.mapped('employees').filtered(lambda e: e.state in ('active', 'onboarding'))
            else:
                affected_employees = empty_employee_recordset

            holiday.affected_employees = affected_employees
            holiday.affected_employees_count = len(affected_employees)
            holiday.affected_employees_count_str = f'{len(affected_employees)} employee(s) affected'

    def day_is_holiday_for_user(self, user, day):
        holiday = self._days_holidays(day, public=True)
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)])
        return holiday.filtered(
            lambda h: h.state_name == employee.work_location_id.state_id and
            h.country_name == employee.work_location_id.country_id)

    def print_on_slack(self, day_descriptor='Today'):
        def display_employees(employees, employees_count):
            if employees_count == 1:
                return employees.name
            if employees_count == 2:
                return employees[0].name + ' and ' + employees[1].name
            if employees_count == 3:
                return employees[0].name + ', ' + employees[1].name + ' and ' + employees[2].name
            
            n = employees_count - 3
            return employees[0].name + ', ' + employees[1].name + ', ' + employees[2].name + f' and {n} more people'

        slack_event_obj = self.env['slack.event']
        affected_employee_action = self.env.ref('addon_hr_customizations.holidays_holiday_affected_employee_action')
        holiday_menu = self.env.ref('addon_holidays.holidays_root_menu')

        for holiday in self:
            affected_employees = holiday.affected_employees
            affected_employees_count = holiday.affected_employees_count

            if not affected_employees_count:
                slack_event_obj.dispatch(
                    'today_is_public_holiday',
                    {
                        'holiday': holiday,
                        'day_descriptor': day_descriptor,
                        'employees': False
                    }
                )
                continue

            employees = display_employees(affected_employees, affected_employees_count)

            verb = 'has' if affected_employees_count == 1 else 'have'

            url = ''
            if affected_employees_count >= 4:
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                url = base_url + f'/web#id={holiday.id}&view_type=tree&model=holidays.holiday'
                url += '&action=%d' % affected_employee_action.id
                url += '&menu_id=%d' % holiday_menu.id

            slack_event_obj.dispatch(
                'today_is_public_holiday',
                {
                    'holiday': holiday,
                    'day_descriptor': day_descriptor,
                    'suffix': f'{verb} a day off to rest',
                    'employees': employees,
                    'url': url,
                    'button_name': 'See who is on Holiday' if url else ''
                }
            )
        return True
