# -*- coding: utf-8 -*-
from odoo import api, fields, models


# we add a new field for the settings and redefine the get and set methods.
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    same_rates_bool = fields.Boolean('Multi - company - same rates', default=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo().get_param('res.config.settings.same.rates.bool')
        res.update(same_rates_bool=param, )
        return res

    @api.multi
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('res.config.settings.same.rates.bool', self.same_rates_bool or False)
        return res
