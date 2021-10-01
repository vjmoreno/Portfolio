# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployeeKanbanColor(models.Model):
    _inherit = 'hr.employee'

    kanban_color = fields.Char(store=True)

    @api.model
    def recompute_employee_kanban_color(self):
        self.search([]).set_employee_kanban_color()

    @api.model
    def create(self, vals):
        employee = super(HrEmployeeKanbanColor, self).create(vals)
        employee.set_employee_kanban_color()
        return employee

    def write(self, vals):
        res = super(HrEmployeeKanbanColor, self).write(vals)
        if vals.get('state'):
            self.set_employee_kanban_color()
        return res

    def set_employee_kanban_color(self):
        for record in self:
            color = 'white'
            if record.state:
                if record.state == 'draft':
                    color = 'rgba(213, 242, 245, 0.5);'
                elif record.state == 'hiring':
                    color = 'rgba(230, 232, 100, 0.5);'
                elif record.state == 'onboarding':
                    color = 'rgba(230, 252, 131, 0.5);'
                elif record.state == 'active':
                    color = 'rgba(255, 255, 255, 1);'
                elif record.state == 'terminated':
                    color = 'rgba(166, 165, 162, 0.5);'
                elif record.state == 'leave_of_absence':
                    color = 'rgba(166, 165, 162, 0.5);'
            
            record.kanban_color = color
