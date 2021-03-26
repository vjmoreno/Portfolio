# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"
    major_distributor_stock = fields.Char('Major distributor', compute='compute_major_distributor_stock')

    @api.depends('seller_ids')
    def compute_major_distributor_stock(self):
        total_stock = 0
        max_distributor_stock = 0
        for distributor in self.env['product.supplierinfo'].search([('product_tmpl_id', '=', self.id)]):
            total_stock += distributor.available_stock
            if distributor.available_stock > max_distributor_stock:
                max_distributor_stock = int(distributor.available_stock)
        self.major_distributor_stock = str(max_distributor_stock) + '/' + str(total_stock)
