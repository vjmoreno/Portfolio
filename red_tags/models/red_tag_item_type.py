# -*- coding: utf-8 -*-
from odoo import models, fields


class ItemType(models.Model):
    _name = 'red.tag.item.type'
    name = fields.Char('Name')
