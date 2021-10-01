# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployeeRelationships(models.Model):

    _name = 'hr.employee.relationships'
    _description = "Relationships"
    _order = 'sequence, id'

    name = fields.Char(string='Relationship', required=True)
    employees = fields.One2many('hr.employee', 'relationships', string='Employees')
    description = fields.Text()
    sequence = fields.Integer(default=1)


class EmployeeRelationships(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def _get_default_relationships(self):
        relationships_obj = self.env.get('hr.employee.relationships')
        if relationships_obj:
            return relationships_obj.search([('name', '=', 'US Employee W2')]).id
        return False

    relationships = fields.Many2one('hr.employee.relationships', default=_get_default_relationships, string='Relationship')
