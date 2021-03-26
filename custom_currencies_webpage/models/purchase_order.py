# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.depends('order_line.invoice_lines.invoice_id')
    def _compute_invoice(self):
        for order in self:
            invoices = self.env['account.invoice']
            for line in order.order_line:
                invoices |= line.invoice_lines.mapped('invoice_id')

            currency_journals = self.env['account.journal'].sudo().search([('type', '=', 'purchase'),
                                                                           ('currency_id', '=', order.currency_id.id),
                                                                           ('company_id', '=',
                                                                            self.env.user.company_id.id),
                                                                           ('active', '=', True)
                                                                           ])
            if len(currency_journals) > 0:
                journal_id = currency_journals[0].id
                for invoice in invoices:
                    invoice.journal_id = journal_id

            order.invoice_ids = invoices
            order.invoice_count = len(invoices)
