# -*- coding: utf-8 -*-
from odoo import models


class PartnerXlsx(models.AbstractModel):
    _name = 'report.nxlog_time_off.hr_leave_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        employees = set([record.employee_id for record in partners])
        leave_types = set([record.holiday_status_id for record in partners])
        leave_types_dict = {leave_type.name: [] for leave_type in leave_types}
        for leave in leave_types:
            name = leave.name
            workbook.add_worksheet(name)
        dates = []
        for record in partners:
            leave_types_dict[record.holiday_status_id.name].append(record)
            if record.date_from and (record.state == 'validate'):
                date = record.date_from.strftime('%m-%Y')
                if date not in dates:
                    dates.append(date)
        headers = ['Name', 'Job title', 'Department', 'Total entitlement days', 'Remaining days']
        headers.extend(dates)
        for sheet in workbook.worksheets():
            col = 0
            for header in headers:
                sheet.write(0, col, header)
                col += 1
            row = 1
            records = leave_types_dict[sheet.get_name()]
            for employee in employees:
                employee_records = [record for record in records if (record.employee_id == employee) and record.state == 'validate']
                employee_dates = set([record.date_from.strftime('%m-%Y') for record in employee_records if (record.leave_type == 'request' and record.date_from)])
                employee_dates_dict = {date: 0 for date in employee_dates}
                total_entitlement = [record.number_of_days for record in employee_records if record.leave_type == 'allocation']
                total_entitlement = sum(total_entitlement)
                remaining_days = [record.number_of_days for record in employee_records if record.leave_type == 'request']
                remaining_days = total_entitlement + sum(remaining_days)
                sheet.write(row, 0, employee.name)
                sheet.write(row, 1, employee.job_id.name)
                sheet.write(row, 2, employee.department_id.complete_name)
                sheet.write(row, 3, total_entitlement)
                sheet.write(row, 4, remaining_days)
                for record in employee_records:
                    if record.leave_type == 'request':
                        employee_dates_dict[record.date_from.strftime('%m-%Y')] += record.number_of_days
                for key in employee_dates_dict.keys():
                    index = headers.index(key)
                    sheet.write(row, index, employee_dates_dict[key])
                row += 1
