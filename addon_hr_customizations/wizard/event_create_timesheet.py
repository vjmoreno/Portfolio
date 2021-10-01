
import datetime
from datetime import timedelta, MAXYEAR

import logging
import time
import uuid

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat

_logger = logging.getLogger(__name__)

VIRTUALID_DATETIME_FORMAT = "%Y%m%d%H%M%S"

def calendar_id2real_id(calendar_id=None, with_date=False):
    """ Convert a "virtual/recurring event id" (type string) into a real event id (type int).
        E.g. virtual/recurring event id is 4-20091201100000, so it will return 4.
        :param calendar_id: id of calendar
        :param with_date: if a value is passed to this param it will return dates based on value of withdate + calendar_id
        :return: real event id
    """
    if calendar_id and isinstance(calendar_id, str):
        res = [bit for bit in calendar_id.split('-') if bit]
        if len(res) == 2:
            real_id = res[0]
            if with_date:
                real_date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT, time.strptime(res[1], VIRTUALID_DATETIME_FORMAT))
                start = datetime.datetime.strptime(real_date, DEFAULT_SERVER_DATETIME_FORMAT)
                end = start + timedelta(hours=with_date)
                return (int(real_id), real_date, end.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
            return int(real_id)
    return calendar_id and int(calendar_id) or calendar_id

class EventCreateTimesheetWizard(models.TransientModel):
    _name = 'event.create.timesheet.wizard'
    _description = 'Timesheet Wizard for Events'

    google_event_id = fields.Many2one('google.event', 'Event', required=True, store=True)

    start = fields.Datetime(related='google_event_id.start', store=True)
    stop = fields.Datetime(related='google_event_id.stop', store=True)
    duration = fields.Float(related='google_event_id.duration', store=True)
    name = fields.Char(related='google_event_id.name', store=True)

    project_id = fields.Many2one('project.project', 'Project', required=True, domain=[('allow_timesheets', '=', True)])
    task_id = fields.Many2one('project.task', 'Task')

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            return {'domain': {
                'task_id': [('project_id', '=', self.project_id.id)]
            }}
        return {'domain': {
            'task_id': []
        }}


    def create_timesheet(self):
        self.ensure_one()
        timesheet_id = self.env['account.analytic.line'].create({
            'task_id': self.task_id and self.task_id.id or False,
            'google_event_id': self.google_event_id.id,
            'project_id': self.project_id.id,
            'employee_id': self.env.user.employee_id.id,
            'unit_amount': self.duration,
            'name': self.name,
            'date': self.start
        })

        self.google_event_id.timesheet_id = timesheet_id.id

        action = self.env.ref('addon_google_integration.action_google_view_event').read()[0]
        return action
