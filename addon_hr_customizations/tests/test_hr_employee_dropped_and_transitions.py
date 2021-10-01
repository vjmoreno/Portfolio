from contextlib import contextmanager

from odoo.tests.common import SavepointCase, Form, tagged


class Test2EmployeeCommon(SavepointCase):

    @classmethod
    def setUpEmployeeCommon(cls):
        # we create a helpdesk user and a manager
        Users = cls.env['res.users'].with_context(tracking_disable=True)
        cls.main_company_id = cls.env.ref('base.main_company').id
        cls.hr_manager = Users.create({
            'company_id': cls.main_company_id,
            'name': 'HR Manager',
            'login': 'hr_manager',
            'email': 'hm@example.com',
            'groups_id': [(6, 0, [cls.env.ref('hr.group_hr_manager').id])]
        })
        cls.hr_user = Users.create({
            'company_id': cls.main_company_id,
            'name': 'HR User',
            'login': 'hr_user',
            'email': 'hu@example.com',
            'groups_id': [(6, 0, [cls.env.ref('hr.group_hr_user').id])]
        })

        # users to use through the various tests
        user_group_base = cls.env.ref('base.group_user')
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
class TestEmployeeTransitions(Test2EmployeeCommon):

    @classmethod
    def setUpClass(cls):
        super(TestEmployeeTransitions, cls).setUpClass()

        cls.setUpEmployeeCommon()

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

    def test_dropped_state(self):
        with self.sudo('hr_manager'):
            states = self.env['hr.employee']._fields['state'].selection
            self.assertFalse('dropped' in states)

    def test_force_state(self):
        states = self.env['hr.employee']._fields['state'].selection
        states.append(states[0])  # To go trough all states
        with self.sudo('hr_manager'):
            for state in states:
                wizard_form = self.env['hr.employee.force.transition.wizard'].create({'employee_id': self.employee_1.id,
                                                                                      'new_state': state[0]})
                wizard_form.force_transition()
                self.assertEqual(self.employee_1.state, state[0])
