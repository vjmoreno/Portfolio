# -*- coding: utf-8 -*-

from odoo import models, fields


class TravelSpecialAssistance(models.Model):
    _name = 'travel.special.assistance'
    _description = 'Travel Special Assistance'

    name = fields.Char()
