from odoo import api, models, fields, _


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    red_tags_slack_channel = fields.Char(string='Slack channel', default="#slack-test")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        res['red_tags_slack_channel'] = \
            self.env['ir.config_parameter'].sudo().get_param(
                'slack_red_tags.red_tags_slack_channel')
        return res

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()

        self.env['ir.config_parameter'].sudo().set_param(
            'slack_red_tags.red_tags_slack_channel', self.red_tags_slack_channel or '')
