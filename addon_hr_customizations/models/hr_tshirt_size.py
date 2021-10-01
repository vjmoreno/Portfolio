from odoo import api, models, fields
from odoo.addons.addon_restful.common import rest_api_model, rest_api_method

@rest_api_model
class HRTShirtSize(models.Model):
    _name = 'hr.tshirt.size'
    _description = 'T-Shirt size'

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Non-Binary')])

    @rest_api_method()
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        return super(HRTShirtSize, self).search(args, offset, limit, order, count)
