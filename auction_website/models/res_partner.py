# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'
    identity_document = fields.Char('Identity document')
    national_id_number = fields.Char('Document number')
    newsletter = fields.Boolean('Newsletter', default=False)
