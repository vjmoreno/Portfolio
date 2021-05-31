# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.payment.controllers.portal import WebsitePayment
from odoo.addons.portal.controllers.portal import CustomerPortal
import logging

_logger = logging.getLogger(__name__)


class CustomerPortal(CustomerPortal):
    MANDATORY_BILLING_FIELDS = ["name", "mobile", "email", "street", "country_id", "identity_document"]
    OPTIONAL_BILLING_FIELDS = ["national_id_number", "newsletter", "company_name"]

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        user_id = request.env.user.id
        Bid = request.env['bid']
        if 'current_lots_count' in counters:
            current_lots = self.get_user_current_lots(Bid, user_id)
            values['current_lots_count'] = len(current_lots)
        if 'assigned_lots_count' in counters:
            assigned_lots = self.get_user_assigned_lots(Bid, user_id)
            values['assigned_lots_count'] = len(assigned_lots)
        if 'confirmed_lots_count' in counters:
            confirmed_lots = self.get_user_confirmed_lots(Bid, user_id)
            values['confirmed_lots_count'] = len(confirmed_lots)
        return values

    def get_user_current_lots(self, Bid, user_id):
        user_bids = Bid.sudo().search([('user_id', '=', user_id)])
        current_bids = [user_bid for user_bid in user_bids if user_bid.lot_id.is_in_process()]
        current_bids = list(filter(lambda bid: bid == bid.lot_id.current_bid_id, current_bids))
        current_lots = set([current_bid.lot_id for current_bid in current_bids])
        current_lots = list(filter(lambda lot: lot.auction_id and lot.is_published, current_lots))
        return current_lots

    def get_user_assigned_lots(self, Bid, user_id):
        assigned_bids = Bid.sudo().search([('user_id', '=', user_id), ('state', '=', 'assigned')])
        assigned_bids = list(filter(lambda bid: bid == bid.lot_id.current_bid_id, assigned_bids))
        assigned_lots = set([assigned_bid.lot_id for assigned_bid in assigned_bids])
        assigned_lots = list(filter(lambda lot: lot.auction_id and lot.is_published, assigned_lots))
        return assigned_lots

    def get_user_confirmed_lots(self, Bid, user_id):
        confirmed_bids = Bid.sudo().search([('user_id', '=', user_id), ('state', '=', 'confirmed')])
        confirmed_bids = list(filter(lambda bid: bid == bid.lot_id.current_bid_id, confirmed_bids))
        confirmed_lots = set([confirmed_bid.lot_id for confirmed_bid in confirmed_bids])
        confirmed_lots = list(filter(lambda lot: lot.auction_id and lot.is_published, confirmed_lots))
        return confirmed_lots

    @http.route('/my/current-lots', website=True, auth='public')
    def current_lots(self):
        Bid = request.env['bid']
        user_id = request.env.user.id
        current_lots = self.get_user_current_lots(Bid, user_id)
        return request.render('auction_website.portal_lots', {'lots': current_lots,
                                                              'title': 'Current lots'})

    @http.route('/my/assigned-lots', website=True, auth='public')
    def assigned_lots(self):
        Bid = request.env['bid']
        user_id = request.env.user.id
        assigned_lots = self.get_user_assigned_lots(Bid, user_id)
        return request.render('auction_website.portal_lots', {'lots': assigned_lots,
                                                              'title': 'Assigned lots'})

    @http.route('/my/confirmed-lots', website=True, auth='public')
    def confirmed_lots(self):
        Bid = request.env['bid']
        user_id = request.env.user.id
        confirmed_lots = self.get_user_confirmed_lots(Bid, user_id)
        return request.render('auction_website.portal_lots', {'lots': confirmed_lots,
                                                              'title': 'Confirmed lots'})


class WebsitePayment(WebsitePayment):

    @http.route(['/website_payment/pay'], type='http', auth='user', website=True, sitemap=False)
    def pay(self, reference='', order_id=None, amount=False, currency_id=None, acquirer_id=None, partner_id=False,
            access_token=None, **kw):
        account_move_id = request.env['account.move'].search([('payment_reference', '=', reference)], limit=1)
        if account_move_id:
            if account_move_id.state != 'cancel':
                res = super(WebsitePayment, self).pay(reference=reference, order_id=order_id, amount=amount,
                                                      currency_id=currency_id, acquirer_id=acquirer_id,
                                                      partner_id=partner_id,
                                                      access_token=access_token, **kw)
                return res
        else:
            res = super(WebsitePayment, self).pay(reference=reference, order_id=order_id, amount=amount,
                                                  currency_id=currency_id, acquirer_id=acquirer_id,
                                                  partner_id=partner_id,
                                                  access_token=access_token, **kw)
            return res
