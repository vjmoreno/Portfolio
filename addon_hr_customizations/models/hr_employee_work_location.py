from odoo import api, fields, models
from odoo.exceptions import UserError
import requests
import pytz
from odoo.addons.addon_restful.common import rest_api_model, rest_api_method
import time
from urllib.parse import quote_plus
import json
import logging

_logger = logging.getLogger(__name__)

_tzs = [(tz, tz) for tz in sorted(pytz.all_timezones, key=lambda tz: tz if not
tz.startswith('Etc/') else '_')]
MO_FR = set([0, 1, 2, 3, 4])
SA_WE = set([5, 6, 0, 1, 2])
SA_TH = set([5, 6, 0, 1, 2, 3])
SU_TH = set([6, 0, 1, 2, 3])
MO_SA = set([0, 1, 2, 3, 4, 5])
MO_TH_SA = set([0, 1, 2, 3, 5])

WORK_DAYS = {
    'default': MO_FR,
    'sa_we': SA_WE,
    'su_th': SU_TH,
    'mo_sa': MO_SA,
    'mo_th_sa': MO_TH_SA,
    'sa_th': SA_TH
}

WORK_DAYS_PER_COUNTRY = {
    'AF': 'sa_we',
    'BH': 'su_th',
    'BD': 'su_th',
    'BO': 'mo_sa',
    'BN': 'mo_th_sa',
    'CO': 'mo_sa',
    'DJ': 'sa_th',
    'EG': 'su_th',
    'GQ': 'mo_sa',
    'HK': 'mo_sa',
    'IR': 'sa_th',
    'IQ': 'su_th',
    'IL': 'su_th',
    'JO': 'su_th',
    'KW': 'su_th',
    'LY': 'su_th',
    'MV': 'su_th',
    'MY': 'mo_sa',
    'KP': 'mo_sa',
    'OM': 'su_th',
    'PS': 'sa_th',
    'QA': 'su_th',
    'SA': 'su_th',
    'SO': 'sa_th',
    'SD': 'su_th',
    'SY': 'su_th',
    'AE': 'su_th',
    'YE': 'su_th'
}


def _tz_get(self):
    return _tzs


@rest_api_model
class HolidaysHoliday(models.Model):
    _inherit = "holidays.holiday"
    technical_holidays_event_sync = fields.Text(string='Technical Field (Events Sync)')

    def get_public_holiday_for_employee(self, employee_id, date):
        employee = self.env['hr.employee'].browse(employee_id)

        if not employee.work_location_id:
            return False

        if isinstance(date, str):
            date = fields.Date.from_string(date)

        public_holidays = self.search([
            ('is_public', '=', True),
            ('holiday_date', '=', date),
            ('country_name', '=', employee.work_location_id.country_id.id)
        ])

        if employee.work_location_id.state_id and employee.work_location_id.state_id.code != '00':
            public_holidays = public_holidays.filtered(
                lambda h: h.state_name == employee.work_location_id.state_id or not h.state_name
            )

        return public_holidays

    @rest_api_method()
    @api.model
    def is_public_holiday_for_employee(self, employee_id, date):
        return bool(self.get_public_holiday_for_employee(employee_id, date))

    @rest_api_method()
    @api.model
    def is_weekend_for_employee(self, employee_id, date):
        employee = self.env['hr.employee'].browse(employee_id)

        if not employee.work_location_id:
            return False

        if isinstance(date, str):
            date = fields.Date.from_string(date)

        work_days = WORK_DAYS.get(WORK_DAYS_PER_COUNTRY.get(employee.work_location_id.country_id.code, 'default'))
        return date.weekday() not in work_days

    @rest_api_method()
    @api.model
    def employee_is_available(self, employee_id, date):
        employee = self.env['hr.employee'].browse(employee_id)

        if not employee.work_location_id:
            return False

        if isinstance(date, str):
            date = fields.Date.from_string(date)

        try:
            return \
                not self.is_public_holiday_for_employee(employee_id, date) \
                and not self.is_weekend_for_employee(employee_id, date) \
                and not self.env['hr.leave'].action_employee_has_pto(employee_id, date)
        except Exception:
            raise UserError('Please install the Zenefits Time Off module')

    @api.model
    def get_unavailability_message(self, employee_id, date):
        employee_name = self.env['hr.employee'].browse(employee_id).name
        unavailability_message = f'{employee_name} is not available because of '

        if self.is_public_holiday_for_employee(employee_id, date):
            return unavailability_message + 'a public holiday.'

        if self.is_weekend_for_employee(employee_id, date):
            return unavailability_message + 'weekend.'

        if self.env['hr.leave'].action_employee_has_pto(employee_id, date):
            return unavailability_message + 'Paid Time Off.'

        return False

    def search_holidays_event(self, employee_id):
        for item in json.loads(self.technical_holidays_event_sync or '[]'):
            if item.get('employee_id') == employee_id.id and item.get('holiday') == self.id:
                return item
        return False

    def create_holiday_events_on_google_calendar(self):
        self.ensure_one()
        new_events = []
        for employee_id in self.affected_employees:
            if employee_id.user_id and employee_id.user_id.google_account_ids \
                    and employee_id.user_id.is_google_configured:
                google_account = employee_id.user_id.google_account_ids[0]
                google_service = google_account.get_google_service()
                event_name = "Holiday: %s" % self.name
                date_start = self.holiday_date
                date_end = self.holiday_date
                searching_event = self.search_holidays_event(employee_id)
                if not searching_event:
                    # Create Event
                    google_event_id = google_service.create_event(event_name, date_start, date_end,
                                                                  transparency='opaque')
                    new_events.append({
                        'holiday': self.id,
                        'employee_id': employee_id.id,
                        'google_event_id': google_event_id
                    })
                else:
                    # Update Event
                    google_service.update_event(searching_event.get('google_event_id'), summary=event_name,
                                                start_datetime=date_start, end_datetime=date_end)

        return new_events


class HrEmployeeWorkLocation(models.Model):
    _name = "hr.employee.work.location"

    name = fields.Char('Name', required=True)
    street = fields.Char('Street')
    street2 = fields.Char('Street 2')
    city = fields.Char('City', required=True)
    state_id = fields.Many2one('res.country.state', string='State/Province')
    country_id = fields.Many2one(
        'res.country', string='Country', required=True
    )
    zipcode = fields.Char('Zip')
    # Deprecated
    remote = fields.Boolean('Is working from home', default=False)
    tz = fields.Selection(_tz_get, string='Timezone')
    employees = fields.One2many('hr.employee', 'work_location_id', string='Employees')
    employee_id = fields.Many2one('hr.employee', string='Employee home office location')

    longitude = fields.Float('Longitude')
    latitude = fields.Float('Latitude')

    @api.model
    def update_slack_flags(self):
        employees = self.env['hr.employee'].search([('work_location_id', '!=', False), ('user_id', '!=', False)])
        employee_users = employees.mapped('user_id')
        employees_per_user = {
            employee.user_id.id: employee for employee in employees
        }
        slack_users = self.env['slack.users.map'].search(
            [('token', '!=', False), ('user_id', 'in', employee_users.ids)])

        data = []
        for slack_user in slack_users:
            data.append({
                'id': slack_user.slack_id,
                'token': slack_user.token,
                'country_code': employees_per_user[slack_user.user_id.id].work_location_id.country_id.code
            })

        slack_base_url = self.env['ir.config_parameter'].sudo().get_param('slack.base_url',
                                                                          'https://flfoez3tf5.execute-api.us-east-1.amazonaws.com/Stage')
        requests.post(
            f'{slack_base_url}/slack/status',
            json={'users': data}
        )

        return True

    @api.onchange('country_id')
    def get_blank_state(self):
        states = self.env['res.country.state']
        if bool(self.country_id):
            self.state_id = states.search([('name', '=', 'Blank'), ('country_id', '=', self.country_id.id)])

    @api.model
    def work_location_blank_state(self):
        work_locations = self.env['hr.employee.work.location'].search([])
        states = self.env['res.country.state']
        for work_location in work_locations:
            if bool(work_location.state_id) is False:
                work_location.state_id = states.search(
                    [('name', '=', 'Blank'), ('country_id', '=', work_location.country_id.id)])

    @api.model
    def set_unset_timezones(self):
        for work_location in self.search([('tz', '=', False)]):
            work_location.get_timezone()

        address_home_ids = self.env['hr.employee'].search([('address_home_id', '!=', False)]).mapped('address_home_id')
        for contact in address_home_ids.filtered(lambda rec: rec.tz is False):
            contact.get_timezone()

        return True

    #  Deprecated method
    def _get_timezone(self):
        api_key = self.env['ir.config_parameter'].sudo().get_param(
            'timezone_api_key', False)
        if api_key:
            for work_location in self:
                location = []
                location.append(work_location.city)
                if work_location.state_id:
                    location.append(work_location.state_id.name)
                location.append(work_location.country_id.name)
                location = ','.join(location)
                timezone_json = requests.get(
                    f'https://api.ipgeolocation.io/timezone?apiKey'
                    f'={api_key}&location={location}'
                )
                try:
                    work_location.tz = timezone_json.json()['timezone']
                except (ValueError, KeyError):
                    pass

                employees = self.env['hr.employee'].search([
                    ('work_location_id', '=', work_location.id)
                ])
                employees.update_user_tz_based_on_work_location()
        return True

    def build_encoded_address(self):
        address = ''

        if self.street:
            address += self.street
        if self.street2:
            address += f' {self.street2}'

        address += (', ' if address else '') + f'{self.city}'

        if self.state_id and self.state_id.name != 'Blank':
            address += f', {self.state_id.code}'
            if self.zipcode:
                address += f' {self.zipcode}'
        elif self.zipcode:
            address += f', {self.zipcode}'

        address += f', {self.country_id.name}'
        return quote_plus(address)

    def get_timezone(self):
        api_key = self.env['ir.config_parameter'].sudo().get_param(
            'google_map_api_key', False)

        if api_key:
            for work_location in self:
                encoded_address = work_location.build_encoded_address()
                geocode_result = requests.get(
                    f'https://maps.googleapis.com/maps/api/geocode/json?'
                    f'address={encoded_address}&key={api_key}'
                ).json()

                if geocode_result['status'] == 'OK':
                    location = geocode_result['results'][0]['geometry']['location']
                    latitude, longitude = location['lat'], location['lng']

                    work_location.longitude = longitude
                    work_location.latitude = latitude

                    timestamp = int(time.time())

                    timezone_result = requests.get(
                        f'https://maps.googleapis.com/maps/api/timezone/json?'
                        f'location={latitude},{longitude}&timestamp={timestamp}&key={api_key}'
                    ).json()

                    if timezone_result['status'] == 'OK':
                        try:
                            work_location.tz = timezone_result['timeZoneId']
                        except (ValueError, KeyError):
                            pass

        employees = self.env['hr.employee'].search([
            ('work_location_id', 'in', self.ids)
        ])
        employees.update_user_tz_based_on_work_location()

        return True

    def ensure_has_country_state(self):
        country_state = self.env['holidays.work.location'].sudo().search([
            ('country_name', '=', self.country_id.id),
            ('state_name', '=', self.state_id.id)
        ])

        if country_state:
            return True

        self.env['holidays.work.location'].sudo().create({
            'country_name': self.country_id.id,
            'state_name': self.state_id.id,
            'name': f'{self.country_id.name}' + (
                f' - {self.state_id.name}' if self.state_id else ''
            )
        })

        return True

    @api.model
    def sync_upcoming_holidays(self):
        self.env['holidays.work.location'].clean_work_locations()

        work_locations = self.env['hr.employee'].search(
            [('state', 'in', ('active', 'onboarding'))]
        ).mapped('work_location_id')

        for work_location in work_locations:
            work_location.ensure_has_country_state()

        countries = work_locations.mapped('country_id')
        states = work_locations.mapped('state_id')
        self.env['holidays.holiday'].sudo()._sync_upcoming_holidays(
            countries, states
        )
        self.sync_holidays_google()
        return True

    def sync_holidays_google(self):
        domain = [('affected_employees_count', '>', 0)]
        holidays = self.env['holidays.holiday'].search(domain)
        for holiday in holidays:
            actually_events = json.loads(holiday.technical_holidays_event_sync or '[]')
            new_events = holiday.create_holiday_events_on_google_calendar()
            holiday.sudo().write({
                'technical_holidays_event_sync': json.dumps(actually_events + new_events)
            })

    # ----------------------------------------------------
    # ORM Overrides
    # ----------------------------------------------------
    @api.model
    def create(self, vals):
        work_location = super(HrEmployeeWorkLocation, self).create(vals)

        #  Load employee's holidays only when he is active
        if work_location.employees.filtered(lambda employee: employee.state in ('active', 'onboarding')):
            self.env['holidays.holiday'].sudo()._sync_upcoming_holidays(
                work_location.country_id, work_location.state_id or
                                          self.env['res.country.state']
            )

        work_location.get_timezone()
        return work_location

    def write(self, vals):
        res = super(HrEmployeeWorkLocation, self).write(vals)
        if vals.get('city') or vals.get('state_id') or vals.get('country_id'):
            self.get_timezone()
        return res

    def unlink(self):
        for rec in self:
            if rec.employee_id:
                rec.employee_id.is_remote = False
        return super(HrEmployeeWorkLocation, self).unlink()


class WorkLocation(models.Model):
    _inherit = "holidays.work.location"

    def has_work_location_associated(self):
        self.ensure_one()
        wl = self.env['hr.employee.work.location'].search([
            ('country_id', '=', self.country_name.id)
        ])
        if self.state_name:
            wl = wl.filtered(lambda work_location: work_location.state_id == self.state_name)
        wl = wl.filtered(
            lambda work_location: work_location.employees.filtered(
                lambda employee: employee.state in ('active', 'onboarding')
            )
        )
        return bool(wl)

    @api.model
    def clean_work_locations(self):
        for work_location in self.search([]):
            if not work_location.has_work_location_associated():
                work_location.unlink()
        return True
