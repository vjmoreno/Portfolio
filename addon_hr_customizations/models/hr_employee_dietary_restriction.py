# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployeeDietaryRestriction(models.Model):
    _name = 'hr.employee.dietary.restriction'
    _description = 'Hr Employee Dietary Restriction'

    name = fields.Char(required=True)
