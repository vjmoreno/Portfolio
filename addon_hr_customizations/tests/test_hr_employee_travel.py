from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install', 'custom', 'addon_hr_customizations')
class TestHrEmployeeTravel(TransactionCase):

    def test_01_hr_employee_travel(self):
        employee_id = self.env['hr.employee'].create({'first_name': 'Test',
                                                      'last_name': '01'})
        pre_check_tsa = '0001'
        seat_preference = 'window'

        employee_id.seat_preference = seat_preference
        self.assertEqual(employee_id.seat_preference, seat_preference)
        employee_id.pre_check_tsa = pre_check_tsa
        self.assertEqual(employee_id.pre_check_tsa, pre_check_tsa)

    def test_02_hr_loyalty_program(self):
        program_ids = self.env['hr.loyalty.program'].search([])
        self.assertTrue(len(program_ids) > 1)

        employee_id = self.env['hr.employee'].create({'first_name': 'Test',
                                                      'last_name': '01',
                                                      'frequent_flyer_ids': [(0, False, {
                                                        'loyalty_program_id': program_ids[0].id,
                                                        'frequent_flyer_no': 'A1'})]})
        self.assertTrue(len(employee_id.frequent_flyer_ids) >= 1)
