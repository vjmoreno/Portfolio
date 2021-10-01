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
            'country_id': self.env['res.country'].search([], limit=1).id,
            'city': 'Test City'
        }
        return self.env['res.partner'].create(data).id

    def test_activate_wizard(self):
        print("UNIT TEST : Activate Employee Wizard")
        employee_id = self.employee_1.id
        self.employee_1.address_home_id = self.create_contact(self.employee_1)

        country_id = self.employee_1.address_home_id.country_id.name
        city = self.employee_1.address_home_id.city

        mail_domain = self.env['nanoramic.email.domain'].create({'name': 'example.com'}).id

        department_id = self.env['hr.department'].search([], limit=1).id
        company_id = self.env['res.company'].search([], limit=1).id
        relationships = self.env.ref('addon_hr_customizations.employee_relationship_1').id
        parent_id = self.env['hr.employee'].search([], limit=1).id

        wizard_form = self.env['hr.employee.activate.wizard'].create({
            'employee_id': employee_id,
            'wizard_step': 3,
            'full_name': 'Employee_1 T',
            'mail': 'my.employee',
            'nanoramic_mail_domain': mail_domain,
            'date_start': date.today(),
            'private_email': self.employee_1.private_email,
            'mail_template': 'TEMPLATE',
            'birthday': date.today(),
            'department_id': department_id,
            'company_id': company_id,
            'relationships': relationships,
            'parent_id': parent_id,
            'skip_mail': True,
        })
        wizard_form.activate_employee()

        self.assertEqual(self.employee_1.address_home_id.country_id.name, country_id)
        self.assertEqual(self.employee_1.address_home_id.city, city)
        self.assertEqual(self.employee_1.birthday, date.today())
        self.assertEqual(self.employee_1.department_id.id, department_id)

    def test_activate_from_draft_wizard(self):
        print("UNIT TEST : Activate Employee Wizard from Draft")
        employee_id = self.employee_1.id
        self.employee_1.address_home_id = self.create_contact(self.employee_1)
        self.employee_1.state = 'draft'
        country_id = self.employee_1.address_home_id.country_id.name
        city = self.employee_1.address_home_id.city

        mail_domain = self.env['nanoramic.email.domain'].create({'name': 'example.com'}).id

        department_id = self.env['hr.department'].search([], limit=1).id
        company_id = self.env['res.company'].search([], limit=1).id
        relationships = self.env.ref('addon_hr_customizations.employee_relationship_1').id
        parent_id = self.env['hr.employee'].search([], limit=1).id

        wizard_form = self.env['hr.employee.activate.wizard'].create({
            'employee_id': employee_id,
            'wizard_step': 3,
            'full_name': 'Employee_1 T',
            'mail': 'my.employee',
            'nanoramic_mail_domain': mail_domain,
            'date_start': date.today(),
            'private_email': self.employee_1.private_email,
            'mail_template': 'TEMPLATE',
            'birthday': date.today(),
            'department_id': department_id,
            'company_id': company_id,
            'relationships': relationships,
            'parent_id': parent_id,
            'skip_mail': True,
        })
        wizard_form.activate_employee()

        self.assertEqual(self.employee_1.address_home_id.country_id.name, country_id)
        self.assertEqual(self.employee_1.address_home_id.city, city)
        self.assertEqual(self.employee_1.birthday, date.today())
        self.assertEqual(self.employee_1.department_id.id, department_id)

    def test_pronoun(self):
        self.employee_1.employee_pronoun = 'he'
        self.employee_1.gender = 'other'
        self.assertEqual(self.employee_1.employee_pronoun, 'he')
        self.assertEqual(dict(self.env['hr.employee']._fields['gender'].selection).get(self.employee_1.gender), 'Non-Binary')