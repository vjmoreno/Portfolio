import datetime
import mock
from odoo.tests import tagged, SingleTransactionCase
import logging

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install', 'addon_hr_customizations', 'post_holiday_events')
class TestPostHolidayEvents(SingleTransactionCase):

    @classmethod
    def setUpClass(self):
        super(TestPostHolidayEvents, self).setUpClass()
        user_group_base = self.env.ref('base.group_user')
        Users = self.env['res.users'].with_context({'no_reset_password': True})
        company_id = self.env['res.company'].search([], limit=1)
        self.user_employee = Users.create({
            'name': 'HR Employee 1',
            'login': 'hr_employee_1',
            'email': 'hr_employee_1@example.com',
            'company_id': company_id.id,
            'company_ids': [(6, 0, [company_id.id])],
            'groups_id': [(6, 0, [user_group_base.id])]
        })

        # here can test for managers, in this case with the user is enough
        user_group_hr_user = self.env.ref('hr.group_hr_user')
        # setup users
        self.user_employee.write({'groups_id': [(4, user_group_hr_user.id)]})

        # Create Employee
        self.employee_1 = self.env['hr.employee'].create({
            'first_name': 'Employee_1',
            'last_name': 'T',
            'private_email': 'testing_hiring@example.com',
            'tz': 'UTC',
            'user_id': self.user_employee.id,
        })
        # Create Holiday
        self.holiday_1 = self.env['holidays.holiday'].create({
            'name': 'Test Holiday 001',
            'holiday_date': datetime.datetime.today(),
            'country_name': self.env['res.country'].search([], limit=1).id,
        })
        self.fake_response_1 = {
            'holiday': self.holiday_1.id,
            'employee_id': self.employee_1.id,
            'google_event_id': 'test01event'
        }

    def test_post_holiday_events(self):
        _logger.info("[addon_hr_customizations] Post Holiday Events")
        fake_response_google_event = mock.MagicMock()
        fake_response_google_event.return_value = self.fake_response_1
        with mock.patch('odoo.addons.addon_hr_customizations.models.hr_employee_work_location.HolidaysHoliday'
                        '.create_holiday_events_on_google_calendar', fake_response_google_event):
            response = self.holiday_1.create_holiday_events_on_google_calendar()
            _logger.info("[addon_hr_customizations] Return Value")
            _logger.info("[addon_hr_customizations] Expected Response: %s" % response)
            _logger.info("[addon_hr_customizations] Received Response: %s" % response)
            self.assertEqual(self.fake_response_1, response)
            _logger.info("[addon_hr_customizations] Post Holiday Events - SUCCEEDED")
