# -*- coding: utf-8 -*-
from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class MarketingEvent(models.Model):

    _sql_constraints = [('date_check', "CHECK ((start_date <= end_date))",
                         "The start date must be anterior to the end date.")]

    _name = 'marketing.event'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Marketing event'
    name = fields.Char('Name', required=True)
    description = fields.Html('Description')
    owner = fields.Many2one('res.users', string='Owner', required=True, default=lambda self: self.env.user)
    start_date = fields.Date('Start date', default=fields.Date.today())
    end_date = fields.Date('End date')

    def write(self, values):
        for marketing_event in self:
            start_date = values['start_date'] if 'start_date' in values.keys() else marketing_event.start_date
            end_date = values['end_date'] if 'end_date' in values.keys() else marketing_event.end_date
            marketing_event.check_dates(start_date, end_date)
            if not marketing_event.end_date and 'end_date' not in values.keys():
                values['end_date'] = values['start_date'] if 'start_date' in values.keys() else marketing_event.start_date
        res = super().write(values)
        return res

    def check_dates(self, start_date, end_date):
        if type(start_date) == str:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if type(end_date) == str:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        if not end_date:
            end_date = start_date
        if start_date > end_date:
            raise ValidationError("The start date must be anterior to the end date.")

    @api.model
    def create(self, values):
        start_date = values['start_date'] if 'start_date' in values.keys() else False
        end_date = values['end_date'] if 'end_date' in values.keys() else False
        self.check_dates(start_date, end_date)
        marketing_event = super().create(values)
        if not marketing_event.end_date:
            marketing_event.end_date = marketing_event.start_date
        return marketing_event
