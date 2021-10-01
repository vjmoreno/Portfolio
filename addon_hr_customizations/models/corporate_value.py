# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.addons.addon_restful.common import rest_api_method, rest_api_model


@rest_api_model
class CorporateValue(models.Model):
    _name = 'corporate.value'
    _description = 'Corporate Value'
    _order = 'sequence, create_date desc'

    name = fields.Char(required=True)
    description = fields.Text('Description')
    sequence = fields.Integer('Sequence')

    @rest_api_method()
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        return super(CorporateValue, self).search(args, offset=offset, limit=limit, order=order, count=count)
