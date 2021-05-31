# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    bid_ids = fields.One2many('bid', 'pricelist_id', string='Bids')
