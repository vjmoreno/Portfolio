# -*- coding: utf-8 -*-
import calendar
import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api


def days_in_month(first_day):
    return calendar.monthrange(first_day.year, first_day.month)[1]


def subtract_years(date, years):
    try:
        # Return same day of the current year
        return date.replace(year=date.year - years)
    except ValueError:
        # If not same day, it will return other, i.e.  February 29 to March 1 etc.
        return date + (date(date.year - years, 1, 1) - date(date.year, 1, 1))


def get_previous_quarter_dates(quarter_first_day, quarter_last_day):
    previous_quarter_first_day = quarter_first_day
    previous_quarter_last_day = quarter_last_day
    for x in range(3):
        previous_quarter_first_day = previous_quarter_first_day - datetime.timedelta(
            days=days_in_month(previous_quarter_first_day + datetime.timedelta(days=-1)))
        previous_quarter_last_day = previous_quarter_last_day - datetime.timedelta(
            days=days_in_month(previous_quarter_last_day))
    return previous_quarter_first_day, previous_quarter_last_day


def get_dates():
    today = datetime.date.today()

    # months dates
    current_month_last_day = (today + relativedelta(months=1)).replace(day=1) - datetime.timedelta(days=1)
    current_month_first_day = today.replace(day=1)
    last_month_last_day = current_month_first_day - datetime.timedelta(days=1)
    last_month_first_day = last_month_last_day.replace(day=1)
    two_month_last_day = last_month_first_day - datetime.timedelta(days=1)
    two_month_first_day = two_month_last_day.replace(day=1)
    three_month_last_day = two_month_first_day - datetime.timedelta(days=1)
    three_month_first_day = three_month_last_day.replace(day=1)

    # quarter dates
    current_quarter = (today.month - 1) // 3 + 1
    current_quarter_first_day = datetime.datetime(today.year, 3 * ((today.month - 1) // 3) + 1, 1)
    current_quarter_last_day = datetime.datetime(today.year + 3 * current_quarter // 12, 3 * current_quarter % 12 + 1,
                                                 1) + datetime.timedelta(days=-1)

    last_quarter_first_day, last_quarter_last_day = get_previous_quarter_dates(current_quarter_first_day,
                                                                               current_quarter_last_day)

    two_quarter_first_day, two_quarter_last_day = get_previous_quarter_dates(last_quarter_first_day,
                                                                             last_quarter_last_day)

    three_quarter_first_day, three_quarter_last_day = get_previous_quarter_dates(two_quarter_first_day,
                                                                                 two_quarter_last_day)

    current_quarter_first_day = current_quarter_first_day.date()
    current_quarter_last_day = current_quarter_last_day.date()
    last_quarter_first_day = last_quarter_first_day.date()
    last_quarter_last_day = last_quarter_last_day.date()
    two_quarter_first_day = two_quarter_first_day.date()
    two_quarter_last_day = two_quarter_last_day.date()
    three_quarter_first_day = three_quarter_first_day.date()
    three_quarter_last_day = three_quarter_last_day.date()

    # year dates
    current_year_first_day = datetime.datetime.now().date().replace(month=1, day=1)
    current_year_last_day = datetime.datetime.now().date().replace(month=12, day=31)
    last_year_first_day = subtract_years(current_year_first_day, 1)
    last_year_last_day = subtract_years(current_year_last_day, 1)
    two_year_first_day = subtract_years(last_year_first_day, 1)
    two_year_last_day = subtract_years(last_year_last_day, 1)
    three_year_first_day = subtract_years(two_year_first_day, 1)
    three_year_last_day = subtract_years(two_year_last_day, 1)

    return {
        'current_month_last_day': current_month_last_day,
        'current_month_first_day': current_month_first_day,
        'last_month_last_day': last_month_last_day,
        'last_month_first_day': last_month_first_day,
        'two_month_last_day': two_month_last_day,
        'two_month_first_day': two_month_first_day,
        'three_month_last_day': three_month_last_day,
        'three_month_first_day': three_month_first_day,
        'current_quarter_last_day': current_quarter_last_day,
        'current_quarter_first_day': current_quarter_first_day,
        'last_quarter_last_day': last_quarter_last_day,
        'last_quarter_first_day': last_quarter_first_day,
        'two_quarter_last_day': two_quarter_last_day,
        'two_quarter_first_day': two_quarter_first_day,
        'three_quarter_last_day': three_quarter_last_day,
        'three_quarter_first_day': three_quarter_first_day,
        'current_year_last_day': current_year_last_day,
        'current_year_first_day': current_year_first_day,
        'last_year_last_day': last_year_last_day,
        'last_year_first_day': last_year_first_day,
        'two_year_last_day': two_year_last_day,
        'two_year_first_day': two_year_first_day,
        'three_year_last_day': three_year_last_day,
        'three_year_first_day': three_year_first_day,
    }


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # method triggered when an invoice could be paid
    @api.multi
    def action_invoice_paid(self):
        res = super(AccountInvoice, self).action_invoice_paid()
        if self.state == 'paid':
            self.update_history(invoice_paid=True)
        return res

    """ 
    This method is triggered once an invoice from a purchase order or a sale order 
    is paid. It update the history of the bought/sold products.
    
    Also, trigger this method from an scheduled action once a month to update the
    history of each product. 
    """

    @api.multi
    def update_history(self, invoice_paid=False):
        dates = get_dates()

        # when the method has been called by a paid invoice
        if invoice_paid:
            invoice_lines = self.env['account.invoice.line'].search([('invoice_id', '=', self.id)])
            lines = [line for line in invoice_lines]
        # when the method has been called by an scheduled action
        else:
            invoices = self.env['account.invoice'].search([('state', '=', 'paid')])
            invoices_lines = [self.env['account.invoice.line'].search([('invoice_id', '=', invoice.id)]) for invoice in
                              invoices]
            templates = []
            lines = []
            for lines_invoice in invoices_lines:
                lines.extend([line for line in lines_invoice])
                templates.extend([line.product_id.product_tmpl_id for line in lines_invoice])
            for template in templates:
                template.sold_current_month = 0
                template.sold_last_month = 0
                template.sold_two_month = 0
                template.sold_three_month = 0
                template.sold_current_cuarter = 0
                template.sold_last_quarter = 0
                template.sold_two_quarter = 0
                template.sold_three_quarter = 0
                template.sold_current_year = 0
                template.sold_last_year = 0
                template.sold_two_year = 0
                template.sold_three_year = 0
                template.purchased_current_month = 0
                template.purchased_last_month = 0
                template.purchased_two_month = 0
                template.purchased_three_month = 0
                template.purchased_current_cuarter = 0
                template.purchased_last_quarter = 0
                template.purchased_two_quarter = 0
                template.purchased_three_quarter = 0
                template.purchased_current_year = 0
                template.purchased_last_year = 0
                template.purchased_two_year = 0
                template.purchased_three_year = 0

        # This algorithm compares the dates of the lines to update the products history
        for line in lines:
            product_template = line.product_id.product_tmpl_id
            invoice = line.invoice_id
            if dates['current_month_first_day'] \
                    <= datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() \
                    <= dates['current_month_last_day']:
                if invoice.type == 'out_invoice':
                    product_template.sold_current_month += line.quantity
                elif invoice.type == 'in_invoice':
                    product_template.purchased_current_month += line.quantity
            elif dates['last_month_first_day'] \
                    <= datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() \
                    <= dates['last_month_last_day']:
                if invoice.type == 'out_invoice':
                    product_template.sold_last_month += line.quantity
                elif invoice.type == 'in_invoice':
                    product_template.purchased_last_month += line.quantity
            elif dates['two_month_first_day'] \
                    <= datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() \
                    <= dates['two_month_last_day']:
                if invoice.type == 'out_invoice':
                    product_template.sold_two_month += line.quantity
                elif invoice.type == 'in_invoice':
                    product_template.purchased_two_month += line.quantity
            elif dates['three_month_first_day'] \
                    <= datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() \
                    <= dates['three_month_last_day']:
                if invoice.type == 'out_invoice':
                    product_template.sold_three_month += line.quantity
                elif invoice.type == 'in_invoice':
                    product_template.purchased_three_month += line.quantity
            if dates['current_quarter_first_day'] \
                    <= datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() \
                    <= dates['current_quarter_last_day']:
                if invoice.type == 'out_invoice':
                    product_template.sold_current_cuarter += line.quantity
                elif invoice.type == 'in_invoice':
                    product_template.purchased_current_cuarter += line.quantity
            elif dates['last_quarter_first_day'] \
                    <= datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() \
                    <= dates['last_quarter_last_day']:
                if invoice.type == 'out_invoice':
                    product_template.sold_last_quarter += line.quantity
                elif invoice.type == 'in_invoice':
                    product_template.purchased_last_quarter += line.quantity
            elif dates['two_quarter_first_day'] \
                    <= datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() \
                    <= dates['two_quarter_last_day']:
                if invoice.type == 'out_invoice':
                    product_template.sold_two_quarter += line.quantity
                elif invoice.type == 'in_invoice':
                    product_template.purchased_two_quarter += line.quantity
            elif dates['three_quarter_first_day'] \
                    <= datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() \
                    <= dates['three_quarter_last_day']:
                if invoice.type == 'out_invoice':
                    product_template.sold_three_quarter += line.quantity
                elif invoice.type == 'in_invoice':
                    product_template.purchased_three_quarter += line.quantity
            if dates['current_year_first_day'] \
                    <= datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() \
                    <= dates['current_year_last_day']:
                if invoice.type == 'out_invoice':
                    product_template.sold_current_year += line.quantity
                elif invoice.type == 'in_invoice':
                    product_template.purchased_current_year += line.quantity
            elif dates['last_year_first_day'] \
                    <= datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() \
                    <= dates['last_year_last_day']:
                if invoice.type == 'out_invoice':
                    product_template.sold_last_year += line.quantity
                elif invoice.type == 'in_invoice':
                    product_template.purchased_last_year += line.quantity
            elif dates['two_year_first_day'] \
                    <= datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() \
                    <= dates['two_year_last_day']:
                if invoice.type == 'out_invoice':
                    product_template.sold_two_year += line.quantity
                elif invoice.type == 'in_invoice':
                    product_template.purchased_two_year += line.quantity
            elif dates['three_year_first_day'] \
                    <= datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d').date() \
                    <= dates['three_year_last_day']:
                if invoice.type == 'out_invoice':
                    product_template.sold_three_year += line.quantity
                elif invoice.type == 'in_invoice':
                    product_template.purchased_three_year += line.quantity
