# -*- coding: utf-8 -*-
from odoo import fields, models


class AllocationRequest(models.Model):
    _inherit = 'allocation.request'

    return_reason = fields.Text('Return reason')

    def action_return(self):
        self.ensure_one()
        return {
            'name': 'Return',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'return.personal.equipment.wizard',
            'type': 'ir.actions.act_window',
            'context': {'default_allocation_request_id': self.id,
                        'default_equipment_id': self.equipment_id.id,
                        'default_return_to': self.return_to.id,
                        'default_close_date': self.close_date,
                        'default_return_reason': self.return_reason},
            'target': 'new',
        }
