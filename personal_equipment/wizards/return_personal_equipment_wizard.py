# -*- coding: utf-8 -*-
from odoo import fields, models


class ReturnPersonalEquipmentWizard(models.TransientModel):
    _name = 'return.personal.equipment.wizard'
    return_reason = fields.Text('Return reason', required=True)
    close_date = fields.Date('Return date', required=True, default=fields.Date.today())
    return_to = fields.Many2one('res.users', 'Return to', required=True)
    equipment_id = fields.Many2one('maintenance.equipment', 'Equipment', required=True, readonly=True)
    allocation_request_id = fields.Many2one('allocation.request', 'Allocation request', required=True)

    def action_return(self):
        self.allocation_request_id.write({
            'return_reason': self.return_reason,
            'close_date': self.close_date,
            'return_to': self.return_to.id,
            'equipment_id': self.equipment_id.id,
        })
        self.allocation_request_id.set_returned()
