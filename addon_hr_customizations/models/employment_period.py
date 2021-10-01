# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class EmploymentPeriod(models.Model):
    _name = 'employment.period'
    _description = 'Employment Period'

    name = fields.Char(default='/')
    sequence = fields.Integer('Sequence', default=10)
    start_date = fields.Date('Start Date', required=True)
    termination_date = fields.Date('Termination Date')
    termination_reason = fields.Text('Termination Reason')
    relationship_id = fields.Many2one('hr.employee.relationships', 'Relationship', required=True, index=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, ondelete='cascade', index=True)

    @api.constrains('start_date', 'termination_date', 'employee_id')
    def _check_overlapping_periods(self):
        for period in self:
            if self.search_count([('start_date', '<=', period.termination_date), ('termination_date', '>=', period.start_date),
                                  ('employee_id', '=', period.employee_id.id), ('id', '!=', period.id)]):
                raise ValidationError('An employee cannot have overlapping employment periods!')

    @api.constrains('termination_date', 'employee_id')
    def _check_opened_period(self):
        for period in self:
            if not period.termination_date and self.search([('termination_date', '=', False), ('id', '!=', period.id),
                                                            ('employee_id', '=', period.employee_id.id)], limit=1):
                raise ValidationError('Only one employment period can be an open period for the employee!')

    @api.constrains('start_date', 'termination_date')
    def _check_start_date_lt_termination_date(self):
        for period in self:
            if period.termination_date and period.start_date >= period.termination_date:
                raise ValidationError('Termination date should be greater than start date!')
