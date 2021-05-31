# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import ValidationError


# We are going to refer as lots, to the product.template records that are linked, or potentially linked to an auction.
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    auction_id = fields.Many2one('auction', 'Auction')
    lot_end_date = fields.Datetime('Lot end date')
    next_link_time = fields.Datetime('Next link time')
    bid_ids = fields.One2many('bid', 'lot_id', string='Bids', copy=True)
    current_bid_id = fields.Many2one('bid', string="Current bid", readonly=1)

    def default_get(self, fields):
        res = super(ProductTemplate, self).default_get(fields)
        if 'list_price' in res.keys():
            res.update({'list_price': 0})
        return res

    @api.onchange('auction_id')
    def onchange_auction_id(self):
        auction = self.env['auction'].search([('id', '=', self.auction_id.id)], limit=1)
        lot = self.env['product.template'].search([('id', '=', self._origin.id)], limit=1)
        if self.auction_id:
            lot.write({'auction_id': auction})
            for lot in auction.lot_ids:
                lot.lot_end_date = auction.calculate_lot_finalization_time(lot)

    @api.model
    def create(self, values):
        if 'auction_id' in values.keys() and not ('current_bid_id' in values.keys()):
            if values['auction_id']:
                values['list_price'] = 0
        if 'auction_id' in values.keys():
            if values['auction_id']:
                auction = self.env['auction'].search([('id', '=', values['auction_id'])], limit=1)
                values['lot_end_date'] = datetime.strptime(str(auction.end_date), '%Y-%m-%d %H:%M:%S')

        res = super(ProductTemplate, self).create(values)
        if 'auction_id' in values.keys():
            if values['auction_id']:
                auction = self.env['auction'].search([('id', '=', values['auction_id'])], limit=1)
                for lot in auction.lot_ids:
                    lot.lot_end_date = auction.calculate_lot_finalization_time(lot)
        return res

    def write(self, values):
        if 'standard_price' in values.keys():
            if values['standard_price'] == 0 and self.auction_id:
                del values['standard_price']
                if 'responsible_id' in values.keys():
                    del values['responsible_id']
                if 'qty_available' in values.keys():
                    del values['qty_available']

        if 'auction_id' in values.keys() and 'current_bid_id' in values.keys():
            if values['auction_id'] != False and values['current_bid_id'] == False:
                values['list_price'] = 0
        elif 'auction_id' in values.keys():
            if values['auction_id'] != False and not self.current_bid_id:
                values['list_price'] = 0
        elif 'current_bid_id' in values.keys():
            if self.auction_id and values['current_bid_id'] == False:
                values['list_price'] = 0
        else:
            if self.auction_id and not self.current_bid_id:
                values['list_price'] = 0

        res = super(ProductTemplate, self).write(values)
        return res

    @api.model
    def get_countdown_time(self, _id):
        lot = self.env['product.template'].search([('id', '=', _id)], limit=1)
        auction = lot.auction_id
        if auction.is_future_auction():
            date = datetime.strptime(str(auction.start_date), '%Y-%m-%d %H:%M:%S')
        else:
            date = datetime.strptime(str(lot.lot_end_date), '%Y-%m-%d %H:%M:%S')
        seconds_since_epoch = int(date.timestamp()) * 1000
        now = datetime.today()
        now = int(now.timestamp()) * 1000
        return seconds_since_epoch, now, lot.is_in_process()

    def get_url(self):
        return '/auctions/' + slug(self.auction_id) + '/lots/' + slug(self)

    def get_standard_price(self, pricelist=False):
        self.ensure_one()
        if self.env.context.get('website_id'):
            current_website = self.env['website'].get_current_website()
            if not pricelist:
                pricelist = current_website.get_current_pricelist()
        try:
            if self.pricelist_id.currency_id.rate:
                return round(self.standard_price * pricelist.currency_id.rate / self.pricelist_id.currency_id.rate, 1)
            else:
                return round(self.standard_price * pricelist.currency_id.rate, 1)
        except:
            return float('inf')

    def _compute_website_url(self):
        super(ProductTemplate, self)._compute_website_url()
        for product in self:
            if product.id:
                if product.auction_id:
                    product.website_url = product.get_url()
                else:
                    product.website_url = "/shop/%s" % slug(product)

    def is_in_process(self):
        if not self.is_future_lot() and not self.finalized():
            return True
        return False

    def is_future_lot(self):
        now = datetime.today()
        if self.auction_id.start_date:
            start = datetime.strptime(str(self.auction_id.start_date), '%Y-%m-%d %H:%M:%S')
            if start > now:
                return True
        return False

    def finalized(self):
        if self.lot_end_date:
            now = datetime.today()
            if self.lot_end_date:
                end = datetime.strptime(str(self.lot_end_date), '%Y-%m-%d %H:%M:%S')
                if now > end:
                    return True
        return False

    def needs_timer(self):
        if (self.is_future_lot() and self.auction_id.starts_in_less_than_n_days()) or (
                self.is_in_process() and self.auction_id.ends_in_less_than_n_days()):
            return True
        return False

    def get_formatted_start_date(self):
        start = datetime.strptime(str(self.auction_id.start_date), '%Y-%m-%d %H:%M:%S')
        auctions_timezone = self.env['ir.config_parameter'].sudo().get_param('auction_website.auction_timezones')
        pytz_timezone = datetime.now(pytz.timezone(auctions_timezone))
        offset = pytz_timezone.utcoffset().total_seconds() / 3600
        start += timedelta(hours=offset)
        date = start.date()
        date = date.strftime("%d-%m-%Y")
        return date

    def get_formatted_end_date(self):
        end = datetime.strptime(str(self.lot_end_date), '%Y-%m-%d %H:%M:%S')
        auctions_timezone = self.env['ir.config_parameter'].sudo().get_param('auction_website.auction_timezones')
        pytz_timezone = datetime.now(pytz.timezone(auctions_timezone))
        offset = pytz_timezone.utcoffset().total_seconds() / 3600
        end += timedelta(hours=offset)
        date = end.date()
        date = date.strftime("%d-%m-%Y")
        return date

    def get_formatted_date(self):
        if self.is_future_lot():
            return 'Comienza ' + self.get_formatted_start_date()
        elif self.is_in_process():
            return 'Finaliza ' + self.get_formatted_end_date()
        else:
            return 'Finalizada'

    def get_formatted_description_sale(self):
        if self.description_sale:
            if len(self.description_sale) > 60:
                return self.description_sale[:60] + '...'
            else:
                return self.description_sale
        else:
            return ''

    @api.model
    def get_import_templates(self):
        return [{
            'label': 'Import template for Lots and Products (product.template)',
            'template': '/auction_website/static/xls/import_templates.zip'
        }]

    @api.model
    def get_lot_price(self, domain, values):
        product_id = values['product_id']
        pricelist_id = values['pricelist_id']
        domain.extend([('id', '=', product_id)])
        lot = self.env['product.template'].search(domain, limit=1)
        pricelist = self.env['product.pricelist'].search([('id', '=', pricelist_id)], limit=1)
        combination = lot._get_first_possible_combination()
        combination_info = lot._get_combination_info(combination=combination, pricelist=pricelist)
        lot_price = combination_info['price']

        if lot.current_bid_id.user_id.id == self.env.user.id:
            ownership = True
        else:
            ownership = False
        # returns price, price + extra, lot ownership (true or false)
        standard_price = lot.get_standard_price(pricelist)
        if standard_price > round(lot_price + lot.auction_id.extra_price, 2):
            next_bid_price = standard_price
        else:
            next_bid_price = round(lot_price + lot.auction_id.extra_price, 2)
        return round(lot_price, 2), next_bid_price, ownership

    @api.model
    def check_bid_request(self, domain, values):
        product_id = values['product_id']
        value = values['value']
        pricelist_id = values['pricelist_id']
        domain.extend([('id', '=', product_id)])
        lot = self.env['product.template'].sudo().search(domain, limit=1)
        price, extra_price, ownership = self.get_lot_price([], {'pricelist_id': pricelist_id, 'product_id': product_id})
        pricelist = self.env['product.pricelist'].search([('id', '=', pricelist_id)], limit=1)
        if value.replace(',', '').replace('.', '').isdigit():
            value = float(value)
        elif value == '':
            value = extra_price
        else:
            return 'Please check the input'
        if lot.is_in_process() and lot.check_bid_value(price, value, pricelist) and lot.is_published:
            values = {'user_id': self.env.user.id,
                      'lot_id': product_id,
                      'value': round(value, 2),
                      'pricelist_id': pricelist_id}
            user_bid = self.env['bid'].search([('user_id', '=', self.env.user.id), ('lot_id', '=', lot.id)], limit=1)
            if user_bid:
                user_bid.write(values)
                bid = user_bid
            else:
                bid = self.env['bid'].create(values)
            lot.current_bid_id = bid
            currency = pricelist.currency_id
            rate = currency.rate
            if rate and lot.pricelist_id.currency_id.rate:
                list_price = round(lot.pricelist_id.currency_id.rate * value / rate, 2)
            elif rate:
                list_price = round(value / rate, 2)
            else:
                list_price = 0
            lot.list_price = list_price
            if lot.check_bid_last_minutes():
                lot.add_extra_time()
            return 'Has ofertado {}'.format(value)
        if not lot.check_bid_value(price, value, pricelist):
            return 'Oferte un monto mayor.'
        if not lot.is_in_process():
            return 'Este lote ha finalizado.'
        if not lot.is_published:
            return 'Este lote no se encuentra publicado.'

    def check_bid_value(self, price, value, pricelist):
        standard_price = self.get_standard_price(pricelist=pricelist)
        if (price < value) and (standard_price <= value):
            return True
        return False

    def check_bid_ownership(self):
        if self.env.user.id == self.current_bid_id.user_id.id:
            return True
        return False

    def check_bid_last_minutes(self):
        # It returns True if the bid is in the last minutes.
        end = datetime.strptime(str(self.lot_end_date), '%Y-%m-%d %H:%M:%S')
        now = datetime.today()
        last_minutes = timedelta(minutes=self.auction_id.last_minutes)
        if (end - now) < last_minutes:
            return True
        return False

    def add_extra_time(self):
        end = datetime.strptime(str(self.lot_end_date), '%Y-%m-%d %H:%M:%S')
        extra_minutes = timedelta(minutes=self.auction_id.extra_minutes)
        self.lot_end_date = end + extra_minutes

    def check_payment_link_email(self):
        now = datetime.today()
        if self.auction_id and self.finalized() and self.current_bid_id and self.is_published:
            # first email
            if not self.next_link_time:
                next_link_time = now
            else:
                next_link_time = datetime.strptime(str(self.next_link_time), '%Y-%m-%d %H:%M:%S.%f')
            if now >= next_link_time:
                # first customer assigned to the lot
                if not self.current_bid_id.state:
                    self.current_bid_id.state = 'assigned'
                    self.update_next_link_time()
                    self.create_invoice()
                    self.send_email()
                # assign lot to next customer
                elif self.current_bid_id.state == 'assigned':
                    self.current_bid_id.state = 'canceled'
                    self.cancel_invoice()
                    self.update_next_link_time()
                    current_bid = self.get_next_bid_id()
                    # if there is a next bid
                    if current_bid:
                        self.current_bid_id = current_bid
                        current_bid.state = 'assigned'
                        self.create_invoice()
                        self.send_email()

    def create_invoice(self):
        fields = self.prepare_invoice_fields()
        account_move = self.env['account.move'].create(fields)
        account_move.action_post()
        self.current_bid_id.account_move_id = account_move

    def cancel_invoice(self):
        self.current_bid_id.account_move_id.button_draft()
        self.current_bid_id.account_move_id.button_cancel()

    def prepare_invoice_fields(self):
        fields = {
            'move_type': 'out_invoice',
            # 'narration': 'Valid until: ' + str(datetime.strptime(str(self.next_link_time), '%Y-%m-%d %H:%M:%S.%f')),
            'partner_id': self.current_bid_id.user_id.partner_id.id,
            'currency_id': self.current_bid_id.pricelist_id.currency_id.id,
            'payment_reference': 'BID' + str(self.current_bid_id.id) + '/LOT' + str(self.id),
            'invoice_date_due': datetime.strptime(str(self.lot_end_date), '%Y-%m-%d %H:%M:%S').date(),
            'invoice_line_ids': [(0, 0, {
                'name': self.name,
                'price_unit': self.current_bid_id.value,
                'quantity': 1.0,
                'product_id': self.product_variant_id.id,
            })],
        }
        return fields

    def update_next_link_time(self):
        self.next_link_time = datetime.today() + timedelta(days=self.auction_id.time_between_payment_links)

    def get_next_bid_id(self):
        min_diff = float('inf')
        next_bid_id = None
        for bid in self.bid_ids:
            if bid.value < self.current_bid_id.value and (self.current_bid_id.value - bid.value) < min_diff:
                next_bid_id = bid
                min_diff = self.current_bid_id.value - bid.value
        return next_bid_id

    def send_email(self):
        account_move_id = self.current_bid_id.account_move_id
        payment = self.env['payment.link.wizard'].create(
            {'account_move_id': account_move_id.id, 'description': account_move_id.payment_reference,
             'res_id': account_move_id.id,
             'res_model': 'account.move', 'amount': account_move_id.amount_residual,
             'currency_id': account_move_id.currency_id.id, 'partner_id': account_move_id.partner_id.id, })
        payment._generate_link()
        domain = [('name', 'ilike', 'Invoice: Send payment link')]
        template = self.env['mail.template'].search(domain, limit=1)
        if template:
            template.send_mail(payment.id, force_send=True)
            
