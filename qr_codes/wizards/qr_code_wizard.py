from odoo import models, fields, api


class QRCodeWizard(models.TransientModel):
    _name = 'qr.code.wizard'
    qr_code = fields.Many2one('qr.code', string="QR code", required=True)
    res_reference = fields.Reference(selection='_select_target_model', string="Source Document")

    @api.model
    def _select_target_model(self):
        return [('maintenance.equipment', 'Equipment'), ('red.tag', 'Red Tags')]

    def link_qr_code(self):
        self.qr_code.res_reference = self.res_reference
        return {
            'name': 'Link',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'qr.code',
            'res_id': self.qr_code.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            }
