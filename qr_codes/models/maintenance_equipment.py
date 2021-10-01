# -*- coding: utf-8 -*-
from odoo import api, models, fields


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    qr_code_id = fields.Many2one('qr.code', string="QR code")

    '''
    We update the qr_code_id.res_reference here instead of 
    in the write() method because it produces an infinite 
    loop. We are already calling the write() method of 
    this model from the write() method of  the qr.code model.
    '''

    @api.onchange('qr_code_id')
    def onchange_qr_code_id(self):
        if self._origin.id:
            if self.qr_code_id:
                self.qr_code_id.write({'res_reference': 'maintenance.equipment,' + str(self._origin.id)})
                last_qr_code = self.env['qr.code'].search(
                    [('res_reference', '=', 'maintenance.equipment,' + str(self._origin.id)),
                     ('id', '!=', self.qr_code_id.id)])
            else:

                last_qr_code = self.env['qr.code'].search(
                    [('res_reference', '=', 'maintenance.equipment,' + str(self._origin.id))], limit=1)
            last_qr_code.res_reference = False

    @api.model
    def create(self, values):
        res = super().create(values)
        if res.qr_code_id:
            res.qr_code_id.write({'res_reference': 'maintenance.equipment,' + str(res.id)})
        return res
