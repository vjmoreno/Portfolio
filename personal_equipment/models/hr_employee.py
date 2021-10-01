# -*- coding: utf-8 -*-
from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    personal_equipment_count = fields.Integer('Equipment', compute='compute_personal_equipment_count')

    def get_equipment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Equipment',
            'view_mode': 'tree',
            'res_model': 'allocation.request',
            'domain': [('request_user_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_personal_equipment_count(self):
        for record in self:
            record.personal_equipment_count = self.env['allocation.request'].search_count(
                [('request_user_id', '=', self.id)])
