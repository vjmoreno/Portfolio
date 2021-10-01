# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployeeFlag(models.Model):

    _inherit = 'hr.employee'

    flag = fields.Binary(related='country_work_location.image', string="Flag", help="This field holds the icon of the country")