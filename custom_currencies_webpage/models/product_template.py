# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    company_price = fields.Text('Company Price', compute='_compute_company_price')

    @api.depends('list_price')
    def _compute_company_price(self):
        for record in self:
            rate = record.currency_id.rate
            pricelist_list = record.env['product.pricelist'].search([
                ('company_id', '=', record.env.user.company_id.id),
                ('active', '=', True)])

            currencies_list = [pricelist.currency_id for pricelist in pricelist_list]
            currencies_list = list(set(currencies_list))

            record.company_price = ''
            for currency in currencies_list:
                currency_rate = currency.rate
                if rate != 0:
                    record.company_price += currency.symbol + \
                                            ' ' + \
                                            str(round((currency_rate * record.list_price) / rate, 2)) + \
                                            ' ' + \
                                            '\n'
