# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = ['product.template']
    sold_current_month = fields.Integer(string='Current')
    sold_last_month = fields.Integer(string='Last')
    sold_two_month = fields.Integer(string='Two')
    sold_three_month = fields.Integer(string='Three')
    sold_current_cuarter = fields.Integer(string='Current')
    sold_last_quarter = fields.Integer(string='Last')
    sold_two_quarter = fields.Integer(string='Two')
    sold_three_quarter = fields.Integer(string='Three')
    sold_current_year = fields.Integer(string='Current')
    sold_last_year = fields.Integer(string='Last')
    sold_two_year = fields.Integer(string='Two')
    sold_three_year = fields.Integer(string='Three')
    purchased_current_month = fields.Integer(string='Current')
    purchased_last_month = fields.Integer(string='Last')
    purchased_two_month = fields.Integer(string='Two')
    purchased_three_month = fields.Integer(string='Three')
    purchased_current_cuarter = fields.Integer(string='Current')
    purchased_last_quarter = fields.Integer(string='Last')
    purchased_two_quarter = fields.Integer(string='Two')
    purchased_three_quarter = fields.Integer(string='Three')
    purchased_current_year = fields.Integer(string='Current')
    purchased_last_year = fields.Integer(string='Last')
    purchased_two_year = fields.Integer(string='Two')
    purchased_three_year = fields.Integer(string='Three')
