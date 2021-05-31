# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import ValidationError
import pytz

class Auction(models.Model):
    _name = 'auction'
    _rec_name = 'name'
    _sql_constraints = [
        ('date_check', "CHECK ((start_date <= end_date))", "The start date must be anterior to the end date."),
        ('minutes_between_finalizations_check', "CHECK ( minutes_between_finalizations >= 0 )",
         "The minutes between finalizations must be equal to or greater than 0."),

    ]

    @api.model
    def _default_auction_status_id(self):
        return self.env['auction.status'].search([('title', '=', 'Process')], limit=1)

    name = fields.Char('Name', required=True)
    description = fields.Text(required=True)
    #start_date = fields.Datetime('Start Date', required=True, default=fields.Datetime.today())
    start_date = fields.Datetime(required=True)
    end_date = fields.Datetime(required=True)
    auction_status_id = fields.Many2one('auction.status', default=_default_auction_status_id)
    product_category_id = fields.Many2one('product.category', required=True)
    product_public_category_id = fields.Many2one('product.public.category', required=True)
    lot_ids = fields.One2many('product.template', 'auction_id', copy=False)
    image = fields.Binary()
    minutes_between_finalizations = fields.Integer(default=0)
    extra_minutes = fields.Integer(default=0)
    last_minutes = fields.Integer(default=0)
    extra_price = fields.Integer(default=0)
    time_between_payment_links = fields.Integer()

    @api.onchange('lot_ids', 'minutes_between_finalizations', 'end_date')
    def onchange_lot_ids(self):
        for lot in self.lot_ids:
            lot.lot_end_date = self.calculate_lot_finalization_time(lot)

    def calculate_lot_finalization_time(self, lot):
        for x in range(len(self.lot_ids)):
            if lot == self.lot_ids[x]:
                return datetime.strptime(str(self.end_date), '%Y-%m-%d %H:%M:%S') - \
                       x * timedelta(minutes=self.minutes_between_finalizations)

    @api.model
    def get_countdown_time(self, _id):
        auction = self.env['auction'].search([('id', '=', _id)], limit=1)
        end_date = auction.get_max_lot_end_time()
        if auction.is_future_auction():
            date = datetime.strptime(str(auction.start_date), '%Y-%m-%d %H:%M:%S')
        else:
            date = end_date
        seconds_since_epoch = int(date.timestamp()) * 1000
        now = datetime.today()
        now = int(now.timestamp()) * 1000
        return seconds_since_epoch, now, auction.is_in_process()

    @api.model
    def get_countdown_now(self):
        now = datetime.today()
        return int(now.timestamp()) * 1000

    def get_max_lot_end_time(self):
        end_date = datetime.strptime(str(self.end_date), '%Y-%m-%d %H:%M:%S')
        for lot in self.lot_ids:
            if lot.lot_end_date:
                lot_end = datetime.strptime(str(lot.lot_end_date), '%Y-%m-%d %H:%M:%S')
                if lot_end > end_date:
                    end_date = lot_end
        return end_date

    def get_qty_of_lots(self):
        qty = 0
        for lot in self.lot_ids:
            if lot.is_published:
                qty += 1
        return qty

    def get_url(self):
        return '/auctions/' + slug(self) + '/lots'

    def is_in_process(self):
        if not self.is_future_auction() and not self.finalized():
            return True
        return False

    def is_logged_in(self):
        if self.env.user.id == self.env.ref('base.public_user').id:
            return False
        return True

    def finalized(self):
        now = datetime.today()
        end = self.get_max_lot_end_time()
        if end:
            if now > end:
                return True
        return False

    def starts_in_less_than_n_days(self, n=3):
        if self.end_date:
            start = datetime.strptime(str(self.start_date), '%Y-%m-%d %H:%M:%S')
            now = datetime.today()
            n_days_from_now = now + timedelta(days=n)
            if n_days_from_now > start:
                return True
            return False

    def ends_in_less_than_n_days(self, n=3):
        if self.end_date:
            end = datetime.strptime(str(self.end_date), '%Y-%m-%d %H:%M:%S')
            n_days_from_now = datetime.today() + timedelta(days=n)
            if n_days_from_now > end:
                return True
            return False

    def get_formatted_start_date(self):
        start = datetime.strptime(str(self.start_date), '%Y-%m-%d %H:%M:%S')
        auctions_timezone = self.env['ir.config_parameter'].sudo().get_param('auction_website.auction_timezones')
        pytz_timezone = datetime.now(pytz.timezone(auctions_timezone))
        offset = pytz_timezone.utcoffset().total_seconds() / 3600
        start += timedelta(hours=offset)
        date = start.date()
        date = date.strftime("%d-%m-%Y")
        return date

    def get_formatted_end_date(self):
        end = datetime.strptime(str(self.end_date), '%Y-%m-%d %H:%M:%S')
        auctions_timezone = self.env['ir.config_parameter'].sudo().get_param('auction_website.auction_timezones')
        pytz_timezone = datetime.now(pytz.timezone(auctions_timezone))
        offset = pytz_timezone.utcoffset().total_seconds() / 3600
        end += timedelta(hours=offset)
        date = end.date()
        date = date.strftime("%d-%m-%Y")
        return date

    def get_formatted_date(self):
        if self.is_future_auction():
            return 'Comienza ' + self.get_formatted_start_date()
        elif self.is_in_process():
            return 'Finaliza ' + self.get_formatted_end_date()
        else:
            return 'Finalizada'

    def is_future_auction(self):
        now = datetime.today()
        if self.start_date:
            start = datetime.strptime(str(self.start_date), '%Y-%m-%d %H:%M:%S')
            if start > now:
                return True
        return False

    def needs_timer(self):
        if (self.is_future_auction() and self.starts_in_less_than_n_days()) or (
                self.is_in_process() and self.ends_in_less_than_n_days()):
            return True
        return False
