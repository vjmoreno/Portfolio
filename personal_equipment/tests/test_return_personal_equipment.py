from odoo.tests.common import TransactionCase, tagged


@tagged('-at_install', 'post_install')
class TestReturnPersonalEquipment(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestReturnPersonalEquipment, self).setUp(*args, **kwargs)
        self.test_equipment_category = self.env['maintenance.equipment.category'].create({'name': 'Test allocation request'})
        self.test_product = self.env['product.product'].create({'name': 'test'})
        self.test_equipment = self.env['maintenance.equipment'].create({'name': 'test', 'product_id': self.test_product.id})
        self.test_allocation = self.env['allocation.request'].create({'name': 'Test allocation request',
                                                                      'category_id': self.test_equipment_category.id,
                                                                      'equipment_id': self.test_equipment.id,
                                                                      'state': 'allocated'})

    def test_return_personal_equipment(self):
        return_wizard = self.env['return.personal.equipment.wizard'].create({'allocation_request_id': self.test_allocation.id,
                                                                             'return_reason': 'Testing return reason',
                                                                             'close_date': '2021-09-10 18:23:10',
                                                                             'return_to': self.env.user.id,
                                                                             'equipment_id': self.test_allocation.equipment_id.id})
        return_wizard.action_return()
        self.assertEqual(self.test_allocation.state, 'returned', 'The state should be returned')
