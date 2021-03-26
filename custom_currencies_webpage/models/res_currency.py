# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)
'''
This  script contains the necessary changes to 
keep the same rates for all companies. It does
not require any additional changes. To 
activate the method that keeps the rates 
synchronized, the user has to activate the new 
option that appears in: 
settings -> 
general settings ->
Multi - companies -> 
Multi - company - same rates.
'''


class CurrencyRate(models.Model):
    _inherit = "res.currency.rate"
    # field created to prevent recursive creations of records
    created_inside_create_method = fields.Boolean(default=False)

    @api.model
    def create(self, res):
        res_currency_rate = super(CurrencyRate, self).create(res)
        same_rates_bool = self.env['ir.config_parameter'].sudo().get_param('res.config.settings.same.rates.bool')

        if same_rates_bool == 'True':
            same_rates_bool = True
        else:
            same_rates_bool = False
        """
        if the record has not been created inside the create method and the user has selected
        to have the same rates for his companies.
        """
        if not res_currency_rate.created_inside_create_method and same_rates_bool:
            self.sync_company_rates(res_currency_rate)

        return res_currency_rate

    @api.multi
    def write(self, values):
        res_currency_rate = super(CurrencyRate, self).write(values)
        same_rates_bool = self.env['ir.config_parameter'].sudo().get_param('res.config.settings.same.rates.bool')

        if same_rates_bool == 'True':
            same_rates_bool = True
        else:
            same_rates_bool = False
        """
        if the record has not been created inside the create method and the user has selected
        to have the same rates for his companies.
        """

        if not self.created_inside_create_method and same_rates_bool:
            self.sync_company_rates(self)

        return res_currency_rate

    def sync_company_rates(self, res_currency_rate):

        companies = self.env['res.company'].sudo().search([])
        companies_id = [company.id for company in companies]
        last_company_id = max(companies_id)

        date = res_currency_rate.name
        currency_id = res_currency_rate.currency_id.id
        res_currency_rate_rate = res_currency_rate.rate
        # we want to get the rates for each company
        for company_id in range(1, last_company_id + 1):
            # company rates for this currency
            company_rates = self.env['res.currency.rate'].sudo().search([('company_id', '=', company_id),
                                                                         ('currency_id', '=', currency_id)])
            edit = False
            for rate in company_rates:
                # rate is already created
                if rate.name == date and rate.rate == res_currency_rate_rate:
                    _logger.debug('not edit, equal')
                    edit = True
                # edit rate
                elif rate.name == date:
                    edit = True
                    rate.rate = res_currency_rate_rate
                    search_rate = self.env['res.currency.rate'].sudo().search([('id', '=', rate.id)])
                    _logger.debug('edit rate %s, %s', rate, search_rate)
                # edit date
                elif rate.rate == res_currency_rate_rate:
                    edit = True
                    rate.name = date
                    search_rate = self.env['res.currency.rate'].sudo().search([('id', '=', rate.id)])
                    _logger.debug('edit date %s, %s', rate, search_rate)
            # if a record have not been edited, then we create a new one
            if not edit:
                _logger.debug('not edit, create %s')
                created_rate = self.env['res.currency.rate'].sudo().create({'name': date,
                                                                            'currency_id': currency_id,
                                                                            'rate': res_currency_rate_rate,
                                                                            'company_id': company_id,
                                                                            'created_inside_create_method': True})
                created_rate.created_inside_create_method = False
