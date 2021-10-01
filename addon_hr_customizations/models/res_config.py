from odoo import models, fields, tools


class ResCompany(models.Model):
    _inherit = "res.company"

    mail_domain = fields.Char('Mail Domains')

    def _register_hook(self):
        columns = tools.table_columns(self._cr, self._table)
        if 'mail_domain' not in columns:
            tools.create_column(self._cr, self._table, 'mail_domain', 'CHAR')


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    timezone_api_key = fields.Char(
        string='Timezone API Key',
        config_parameter='timezone_api_key'
    )
    google_map_api_key = fields.Char(
        string='Google Map API Key',
        config_parameter='google_map_api_key'
    )
    mail_domain = fields.Char(related="company_id.mail_domain", readonly=False, string='Mail Domain')
