# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.addons.addon_restful.common import rest_api_model, rest_api_method


@rest_api_model
class QRCode(models.Model):
    _sql_constraints = [
        ('qr_code_unique', 'unique(qr_code)', 'The QR code must be unique.')]

    _name = 'qr.code'
    _rec_name = 'qr_code'
    qr_code = fields.Char('QR code', required=True)
    status_options = [('registered', 'Registered'), ('voided', 'Voided')]
    status = fields.Selection(status_options, 'Status', readonly=True, force_save=True)
    res_reference = fields.Reference(selection='_select_target_model', string="Source Document")

    @api.model
    def _select_target_model(self):
        return [('maintenance.equipment', 'Equipment'), ('red.tag', 'Red Tags')]

    def register(self):
        self.status = 'registered'

    def void(self):
        self.status = 'voided'

    def write(self, values):
        if 'res_reference' in values.keys():
            if self.res_reference:
                self.res_reference.write({'qr_code_id': False})
                self.status = False
            if values['res_reference']:
                record_model, record_id = values['res_reference'].split(',')
                if record_model and record_id.isdigit():
                    self.env[record_model].search([('id', '=', record_id)]).write({'qr_code_id': self})
                    self.register()
        res = super().write(values)
        return res

    def unlink(self):
        for qr_code in self:
            if qr_code.status != 'voided':
                raise UserError("You cannot delete a QR code that hasn't been voided.")
        return super(QRCode, self).unlink()

    @rest_api_method()
    @api.model
    def create(self, values):
        if 'res_reference' in values.keys():
            if values['res_reference']:
                accepted_models = list(list(zip(*self._select_target_model()))[0])
                record_model, record_id = values['res_reference'].split(',')
                res_reference = self.env[record_model].search([('id', '=', record_id)], limit=1)
                if record_model in accepted_models and res_reference and not res_reference.qr_code_id:
                    res = super().create(values)
                    res_reference.write({'qr_code_id': res.id})
                    res.register()
                    return res
                else:
                    raise ValidationError('QR code already linked or res_model not accepted.')
            else:
                res = super().create(values)
                return res
        else:
            res = super().create(values)
            return res

    @rest_api_method()
    def get_qr_code(self, qr_code):
        qr_code = self.env['qr.code'].search([('qr_code', '=', qr_code)], limit=1)
        if qr_code:
            return {
                'message': 'QR code found.',
                'qr_code_id': qr_code.id,
                'qr_code': qr_code.qr_code,
                'status': qr_code.status,
                'res_reference': qr_code.res_reference._name + ',' + str(qr_code.res_reference.id)
                if qr_code.res_reference else False
            }
        else:
            return {
                'message': 'QR code not found.',
            }

    @rest_api_method()
    def get_res_reference(self, res_reference):
        accepted_models = list(list(zip(*self._select_target_model()))[0])
        record_model, record_id = res_reference.split(',')
        if record_model in accepted_models:
            res_reference = self.env[record_model].search([('id', '=', record_id)])
            if res_reference:
                return {
                    'res_id': res_reference.id,
                    'res_model': res_reference._name,
                    'qr_code': res_reference.qr_code_id.qr_code,
                    'qr_code_id': res_reference.qr_code_id.id
                }
            else:
                raise ValidationError('The res_reference ID does not exist.')

        else:
            raise ValidationError('Model not accepted. Please change the res_reference model.')
