# -*- coding: utf-8 -*-

import requests
import time
from urllib.parse import quote_plus


from odoo import api, models


class Partner(models.Model):
    _inherit = 'res.partner'

    def build_encoded_address(self):
        address = ''
        if self.street:
            address += self.street
        if self.street2:
            address += f' {self.street2}'

        address += (', ' if address else '') + f'{self.city}'

        if self.state_id and self.state_id.name != 'Blank':
            address += f', {self.state_id.code}'
            if self.zip:
                address += f' {self.zip}'
        elif self.zip:
            address += f', {self.zip}'

        address += f', {self.country_id.name}'
        return quote_plus(address)

    def get_timezone(self):
        api_key = self.env['ir.config_parameter'].sudo().get_param(
            'google_map_api_key', False)

        if api_key:
            for contact in self:
                encoded_address = contact.build_encoded_address()
                geocode_result = requests.get(
                    f'https://maps.googleapis.com/maps/api/geocode/json?'
                    f'address={encoded_address}&key={api_key}'
                ).json()

                if geocode_result['status'] == 'OK':
                    location = geocode_result['results'][0]['geometry']['location']
                    latitude, longitude = location['lat'], location['lng']

                    timestamp = int(time.time())

                    timezone_result = requests.get(
                        f'https://maps.googleapis.com/maps/api/timezone/json?'
                        f'location={latitude},{longitude}&timestamp={timestamp}&key={api_key}'
                    ).json()

                    if timezone_result['status'] == 'OK':
                        try:
                            contact.tz = timezone_result['timeZoneId']
                        except (ValueError, KeyError):
                            pass

        employees = self.env['hr.employee'].search([('address_home_id', 'in', self.ids)])
        employees.update_user_tz_based_on_work_location()

        return True

        # ----------------------------------------------------
        # ORM Overrides
        # ----------------------------------------------------

    @api.model
    def create(self, vals):
        contact = super(Partner, self).create(vals)
        contact.get_timezone()
        return contact

    def write(self, vals):
        res = super(Partner, self).write(vals)
        if vals.get('city') or vals.get('state_id') or vals.get('country_id'):
            self.get_timezone()
        return res