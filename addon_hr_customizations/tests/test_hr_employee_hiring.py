from contextlib import contextmanager
from datetime import date
from odoo.tests.common import SavepointCase, Form, tagged

@tagged('post_install', '-at_install', 'addon_hr_customizations')
class TestEmployeeHiringCommon(SavepointCase):

    @classmethod
    def setUpEmployeeHiringCommon(cls):

        # users to use through the various tests
        user_group_base = cls.env.ref('base.group_user')
        Users = cls.env['res.users'].with_context({'no_reset_password': True})
        company_id = cls.env['res.company'].search([], limit=1)
        cls.user_employee = Users.create({
            'name': 'HR Employee 1',
            'login': 'hr_employee_1',
            'email': 'hr_employee_1@nanoramic.com',
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
class TestEmployeeHiring(TestEmployeeHiringCommon):

    @classmethod
    def setUpClass(cls):
        super(TestEmployeeHiring, cls).setUpClass()

        cls.setUpEmployeeHiringCommon()

        # here can test for managers, in this case with the user is enough
        user_group_hr_user = cls.env.ref('hr.group_hr_user')
        # setup users
        cls.user_employee.write({'groups_id': [(4, user_group_hr_user.id)]})

        # Create Employee
        cls.employee_1 = cls.env['hr.employee'].create({
            'first_name': 'Employee_1',
            'last_name': 'Hiring',
            'private_email': 'testing_hiring@example.com',
            'tz': 'UTC',
            'user_id': cls.user_employee.id
        })

    def test_hiring_state(self):
        self.assertEqual(self.employee_1.state, 'draft')
        with self.sudo('user_hr_1'):
            self.employee_1.state = 'hiring'
            self.assertEqual(self.employee_1.state, 'hiring')

    def test_hiring_wizard(self):
        print("UNIT TEST : Testing New Hiring Status on Employee")
        department_id = self.env['hr.department'].search([], limit=1).id
        company_id = self.env['res.company'].search([], limit=1).id
        relationships = self.env.ref('addon_hr_customizations.employee_relationship_1').id
        parent_id = self.env['hr.employee'].search([], limit=1).id
        country_id = self.env['res.country'].search([], limit=1).id
        employee_id = self.employee_1.id
        first_name = self.employee_1.first_name
        last_name = self.employee_1.last_name
        personal_email = 'testing_hiring@example.com'

        # Change a field value to show that the form is working
        date_today = date.today()
        wizard_form = self.env['hr.employee.create.wizard'].create({
            'employee_id': employee_id,
            'first_name': first_name,
            'last_name': last_name,
            'job_title': 'new job',
            'department_id': department_id,
            'company_id': company_id,
            'relationships': relationships,
            'parent_id': parent_id,
            'start_date': date_today,
            'personal_email': personal_email,
            'work_location': 'from_home',
            'country_id': country_id,
            'city': 'QA City',
            'action': 'hiring',
        })
        wizard_form.create_employee()

        self.assertEqual(self.employee_1.job_title, 'new job')
        self.assertEqual(self.employee_1.state, 'hiring')
        self.assertEqual(self.employee_1.start_date, date_today)
