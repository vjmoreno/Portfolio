# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('inc_tax_unit_price')
    def onchange_inc_tax_unit_price(self):
        self.ex_tax_unit_price = self.inc_tax_unit_price / (1 + self.tax_id.amount / 100)

    @api.onchange('ex_tax_unit_price')
    def onchange_ex__tax_unit_price(self):
        self.inc_tax_unit_price = self.ex_tax_unit_price * (1 + self.tax_id.amount / 100)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def name_get(self):
        res = super(ResPartner, self).name_get()
        data = []
        for partner in self:
            display_value = ''
            display_value += partner.cust_unique_id or ""
            display_value += ' '
            display_value += partner.name or ""
            display_value += ' '
            display_value += partner.zip or ""
            data.append((partner.id, display_value))
        return data