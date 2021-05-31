# -*- coding: utf-8 -*-
from odoo import models, fields


class SalePaymentLink(models.TransientModel):
    _inherit = "payment.link.wizard"
    account_move_id = fields.Many2one('account.move')

