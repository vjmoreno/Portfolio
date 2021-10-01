from odoo import api, models, fields
from odoo.addons.addon_restful.common import rest_api_model, rest_api_method

@rest_api_model
class HrLanguage(models.Model):
    _name = 'hr.language'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'HR Language'

    name = fields.Char(string='Name', required=True)

    @rest_api_method()
    def search(self, args, offset=0, limit=None, order=None, count=False):
        return super(HrLanguage, self).search(args, offset, limit, order, count)

class HrLanguageLine(models.Model):
    _name = 'hr.language.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'HR Language Line'

    language_id = fields.Many2one('hr.language', 'Language')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    employee_state = fields.Selection(related='employee_id.state', string="State")
