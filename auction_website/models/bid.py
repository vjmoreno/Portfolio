# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Bid(models.Model):
    _name = 'bid'
    user_id = fields.Many2one('res.users', string="User")
    lot_id = fields.Many2one('product.template', string="Lot")
    value = fields.Float('Value')
    pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")
    states = [('assigned', 'Assigned'), ('canceled', 'Canceled'), ('confirmed', 'Confirmed')]
    state = fields.Selection(states, 'State')
    account_move_id = fields.Many2one('account.move', string='Invoice', readonly=1)
    lot_end_date = fields.Datetime(related='lot_id.lot_end_date', store=True)
    auction_id = fields.Many2one(related='lot_id.auction_id', store=True)
    auction_start_date = fields.Datetime(related='auction_id.start_date')

    def name_get(self):
        result = []
        for record in self:
            name = str(record.value) + ' from ' + str(record.user_id.name)
            result.append((record.id, name))
        return result

    @api.onchange('account_move_id')
    def set_account_move_bid_id(self):
        self.account_move_id.bid_id = self._origin.id
