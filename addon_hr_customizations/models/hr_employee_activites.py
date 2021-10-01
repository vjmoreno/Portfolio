from odoo import api, models, fields


class EmployeeActivitiesWizard(models.TransientModel):
    _name = 'hr.employee.activities.wizard'

    employee_id = fields.Many2one('hr.employee')
    supervisor_id = fields.Many2one('hr.employee')
    clicked_button = fields.Char()

    def action_transition(self):
        if self.clicked_button == 'terminate':
            self.employee_id.state = 'terminated'
            self.employee_id.deactiveate_work_user()

        elif self.clicked_button == 'leave':
            self.employee_id.state = 'leave_of_absence'

        activity_query = '''
        UPDATE mail_activity SET user_id = %s  WHERE user_id = %s;
        ''' %(self.supervisor_id.user_id.id,self.employee_id.user_id.id)
        self._cr.execute(activity_query)
        self.notify_assign_employee_activities_to_supervisor()

    def notify_assign_employee_activities_to_supervisor(self):
        self.env['slack.event'].dispatch(
            'assign_employee_activities_to_supervisor',
            {
                'object': self,
                'user': self.supervisor_id.user_id,
                'employee_id': self.employee_id,
                'button_name': ' '
            }
        )
        return True