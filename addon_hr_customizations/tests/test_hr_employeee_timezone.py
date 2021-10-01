from contextlib import contextmanager

from datetime import date
from odoo.tests.common import SavepointCase, Form, tagged


class TestEmployeeActivateCommon(SavepointCase):

    @classmethod
    def setUpEmployeeActivateCommon(cls):

        # users to use through the various tests
        user_group_base = cls.env.ref('base.group_user')
        Users = cls.env['res.users'].with_context({'no_reset_password': True})
        company_id = cls.env['res.company'].search([], limit=1)
        cls.user_employee = Users.create({
            'name': 'HR Employee 1',
            'login': 'hr_employee_1',
            'email': 'hr_employee_1@example.com',
            'company_id': company_id.id,
            'company_ids': [(6, 0, [company_id.id])],
            'groups_id': [(6, 0, [user_group_base.id])]
        })

    @contextmanager
    def sudo(self, login):
        old_uid = self.uid
        try:
            user = self.env['res.users'].sudo().search([('login', '=', login)])
            # switch user
            self.uid = user.id
            self.env = self.env(user=self.uid)
            yield
        finally:
            # back
            self.uid = old_uid
            self.env = self.env(user=self.uid)


@tagged('post_install', '-at_install', 'addon_hr_customizations')
class TestEmployeeActivate(TestEmployeeActivateCommon):

    @classmethod
    def setUpClass(cls):
        super(TestEmployeeActivate, cls).setUpClass()

        cls.setUpEmployeeActivateCommon()

        # here can test for managers, in this case with the user is enough
        user_group_hr_user = cls.env.ref('hr.group_hr_user')
        # setup users
        cls.user_employee.write({'groups_id': [(4, user_group_hr_user.id)]})

        # Create Employee
        cls.employee_1 = cls.env['hr.employee'].create({
            'first_name': 'Employee_1',
            'last_name': 'T',
            'private_email': 'testing_hiring@example.com',
            'tz': 'UTC',
            'user_id': cls.user_employee.id
        })

    def create_contact(self, employee_id):
        data = {
            'name': 'Employee_1 T',
            'function': employee_id.job_title,
            'company_id': employee_id.company_id.id,
            'company_type': 'person',
            'country_id': self.env['res.country'].search([('name', '=', 'Mexico')], limit=1).id,
            'city': 'Colima'
        }
        return self.env['res.partner'].create(data).id

    def create_work_location(self):
        return self.env['hr.employee.work.location'].create({'name': 'Boston HQ',
                                                             'country_id': self.env['res.country'].search([('name', '=','United States')], limit=1).id,
                                                             'city': 'Boston'}).id

    def test_employee_timezone(self):
        print("UNIT TEST : Employee Timezone")

        self.employee_1.address_home_id = self.create_contact(self.employee_1)
        self.employee_1.is_remote = True
        work_location_id = self.create_work_location()
        self.employee_1.work_location_id = work_location_id

        self.env['hr.employee.work.location'].set_unset_timezones()

        self.assertTrue(self.employee_1.address_home_id.tz is not None)
        self.assertTrue(self.employee_1.work_location_id.tz is not None)
        self.assertEqual(self.employee_1.work_location_tz, self.employee_1.address_home_id.tz)
        self.employee_1.is_remote = False
        self.employee_1.work_location_id = work_location_id
        self.assertEqual(self.employee_1.work_location_tz, self.employee_1.work_location_id.tz)
