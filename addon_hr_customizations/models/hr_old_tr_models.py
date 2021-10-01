from odoo import models, api, fields

# Deleting a model is considered an "unstable change"

class HrResponsibility(models.Model):
    _name = 'hr.responsibility'

class HrEmployeeResponsibility(models.Model):
    _name = 'hr.employee.responsibility'
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True
    )

class HrEmployeeTeam(models.Model):
    _name = 'hr.employee.team'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)


class HrRole(models.Model):
    _name = "hr.role"