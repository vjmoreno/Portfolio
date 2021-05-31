from odoo import models, fields, api
import pytz


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    timezones = pytz.all_timezones
    timezones_names = [timezone.lower().replace('/', '_') for timezone in timezones]
    timezones_options = list(zip(timezones_names, timezones))
    timezones_options2 = list(zip(timezones, timezones))
    auction_timezones = fields.Selection(timezones_options2, string='Auction Timezones',
                                         config_parameter='auction_website.auction_timezones')
