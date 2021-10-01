from odoo import api, models, fields

class HrTimesheet(models.Model):
    _inherit = 'account.analytic.line'

    google_event_id = fields.Many2one('google.event', 'Event')


class GoogleEvent(models.Model):
    _inherit = 'google.event'

    timesheet_id = fields.Many2one('account.analytic.line', 'Timesheet', compute="_compute_timesheet_id")

    def _compute_timesheet_id(self):
        for event in self:
            timesheet_id = self.env['account.analytic.line'].search([('google_event_id', '=', event.id), ('employee_id', '=', self.env.user.employee_id.id)], limit=1)
            if timesheet_id:
                event.timesheet_id = timesheet_id.id
            else:
                event.timesheet_id = False
