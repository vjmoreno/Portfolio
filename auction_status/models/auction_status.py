# -*- coding: utf-8 -*-
from odoo import fields, models


class AuctionStatus(models.Model):
    _name = 'auction.status'
    _rec_name = 'title'
    title = fields.Char('Title', required=True)
    description = fields.Text('Description')
