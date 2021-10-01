from odoo import api, fields, models


class EmployeeForceTransition(models.TransientModel):
    _name = 'hr.employee.force.transition.wizard'
    _description = 'Force Employee status transition'

    @api.model
    def _get_new_states(self):
        states = self.env['hr.employee']._fields['state'].selection
        employee_id = self._context and self._context.get('default_employee_id', False)
        employee_id = self.env['hr.employee'].browse([employee_id]) if employee_id else None
        current_state = employee_id.state if employee_id else ''
        return [state for state in states if state[0] != current_state]

    employee_id = fields.Many2one('hr.employee')
    new_state = fields.Selection(selection='_get_new_states')

    def force_transition(self):
        self.employee_id.state = self.new_state
        # Reload required to make sure it is shown the correct states if the user use the button again.
        return {'type': 'ir.actions.client', 'tag': 'reload'}

