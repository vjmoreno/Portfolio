# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.addon_restful.common import rest_api_method, rest_api_model


@rest_api_model
class HrEmployeeEducationLevel(models.Model):

    _name = 'hr.employee.education.level'
    _description = "Education Level"
    _order = 'sequence, id'

    name = fields.Char(string='Education level', required=True)
    employees = fields.One2many('hr.employee', 'education_level', string='Employees')
    description = fields.Text()
    sequence = fields.Integer(default=1)
    type = fields.Selection([('unspecified', 'Unspecified'), ('high-school', 'High School'), ('certification', 'Certification'),
                             ('vocational', 'Vocational'), ('associate-degree', 'Associate Degree'),
                             ('bachelor-degree', 'Bachelor Degree'), ('masters-degree', 'Masters Degree'), ('doctorate', 'Doctorate'),
                             ('professional', 'Professional'), ('some-college', 'Some College'),
                             ('vocational-diploma', 'Vocational Diploma'), ('vocational-degree', 'Vocational Degree'),
                             ('some-high-school', 'Some High School')], 'Type', default='unspecified')

    # ----------------------------------------------------
    # Rest API Endpoints
    # ----------------------------------------------------
    @rest_api_method()
    @api.model
    def get_employee_education_level(self):
        education_level_ids = self.search([])
        return dict((rec.id, rec.name) for rec in education_level_ids)


class HrEmployeeEducation(models.Model):

    _inherit = 'hr.employee'

    education_level = fields.Many2one('hr.employee.education.level', string='Education Level')
