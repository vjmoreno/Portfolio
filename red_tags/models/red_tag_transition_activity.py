# -*- coding: utf-8 -*-
from odoo import models, fields
from .red_tag import STATES


class TransitionActivity(models.Model):
    _inherit = 'transition.activity'
    _name = 'red.tag.transition.activity'
    _rec_name = 'summary'
    _description = 'Red Tag transition activity'

    state = fields.Selection(
        string="Transition to status", selection=STATES,
        required=True, help="This activity will be created when Request moves to the selected state.")
