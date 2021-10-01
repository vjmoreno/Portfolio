# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrLoyaltyProgram(models.Model):
    _name = 'hr.loyalty.program'
    _description = 'HR Loyalty Program'

    name = fields.Char()

    _sql_constraints = [('loyalty_program_name_unique', 'UNIQUE(name)',
                         'Name must be unique!')]


class HrEmployeeFrequentFlyer(models.Model):
    _name = 'hr.employee.frequent.flyer'
    _description = 'Employee Frequent Flyer Program'

    employee_id = fields.Many2one('hr.employee', required=True)
    loyalty_program_id = fields.Many2one('hr.loyalty.program', required=True)
    frequent_flyer_no = fields.Char('hr.loyalty.program', required=True)
