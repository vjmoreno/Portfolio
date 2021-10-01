# -*- coding: utf-8 -*-
from odoo import models, fields


class Reason(models.Model):
    _name = 'red.tag.reason'
    name = fields.Char('Name')
