from odoo import api, fields, models
import calendar
from datetime import datetime, timedelta


def compare_months(request_date_from, request_date_to):
    start_month = datetime.strptime(str(request_date_from), '%Y-%m-%d').strftime('%m')
    end_month = datetime.strptime(str(request_date_to), '%Y-%m-%d').strftime('%m')
    if start_month == end_month:
        return True
    return False


def last_day_of_month(date):
    month = int(datetime.strptime(str(date), '%Y-%m-%d').strftime('%m'))
    year = int(datetime.strptime(str(date), '%Y-%m-%d').strftime('%Y'))
    return calendar.monthrange(year, month)[1]


class HolidaysRequest(models.Model):
    _inherit = 'hr.leave'

    @api.model
    def create(self, values):
        new_values = False
        original_request_date_to = False
        original_date_to = False
        request_first_day_next_month = False
        first_day_next_month = False
        if not compare_months(values.get('request_date_from'), values.get('request_date_to')):
            original_request_date_to = datetime.strptime(str(values.get('request_date_to')), '%Y-%m-%d').date()
            original_date_to = datetime.strptime(str(values.get('date_to')), '%Y-%m-%d %H:%M:%S')
            request_date_from = datetime.strptime(str(values.get('request_date_from')), '%Y-%m-%d').date()
            request_last_day_month = request_date_from.replace(day=last_day_of_month(request_date_from))
            last_day_month = datetime.strptime(str(values.get('date_to')), '%Y-%m-%d %H:%M:%S')
            last_day_month = last_day_month.replace(year=request_last_day_month.year,
                                                    month=request_last_day_month.month,
                                                    day=request_last_day_month.day)
            values.update({'request_date_to': request_last_day_month})
            values.update({'date_to': last_day_month})
            values.update({'number_of_days': self._get_number_of_days(
                datetime.strptime(str(values.get('date_from')), '%Y-%m-%d %H:%M:%S'),
                datetime.strptime(str(values.get('date_to')), '%Y-%m-%d %H:%M:%S'),
                values.get('employee_id'))['days']})
            request_first_day_next_month = (request_last_day_month + timedelta(days=1))
            first_day_next_month = (last_day_month + timedelta(days=1))
            new_values = values

        res = super(HolidaysRequest, self).create(values)
        if new_values and request_first_day_next_month and first_day_next_month:
            new_values.update({'request_date_from': request_first_day_next_month})
            new_values.update({'date_from': first_day_next_month})
            new_values.update({'request_date_to': original_request_date_to})
            new_values.update({'date_to': original_date_to})
            new_values.update({'number_of_days': self._get_number_of_days(
                datetime.strptime(str(new_values.get('date_from')), '%Y-%m-%d %H:%M:%S'),
                datetime.strptime(str(new_values.get('date_to')), '%Y-%m-%d %H:%M:%S'),
                new_values.get('employee_id'))['days']})
            self.env['hr.leave'].create(new_values)
        return res
