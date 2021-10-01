# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrEmployeeTravelDocument(models.Model):

    _name = 'hr.employee.travel'
    _description = 'Employee Travel Documents'

    employee_id = fields.Many2one('hr.employee', required=True)
    document_type = fields.Selection([
        ('passport', 'Passport'),
        ('id', 'ID'),
        ('dhs_cards', 'DHS "Trusted Traveler" cards (Global Entry®, NEXUS, SENTRI, FAST)'),
        ('military_id', 'U.S. Military ID'),
        ('permanent_resident_card', 'Permanent Resident Card'),
        ('border_crossing_card', 'Border Crossing Card'),
        ('dhs_designated_driver', 'DHS-designated enhanced driver\'s license'),
    ], string='Document Type', required=True)
    document_number = fields.Char(string='Document Number', required=True)
    country_id = fields.Many2one('res.country', string="Issuing Country", required=True)
    citizenship = fields.Char(string="Citizenship", required=True)
    issued_date = fields.Date(string="Issue Date", required=True)
    expiry_date = fields.Date(string="Expiry Date", required=True)
    is_international = fields.Boolean(string="Passport International Travel Ready")
    document_file = fields.Binary(string='Document', attachment=True, required=True)
    document_name = fields.Char()

    @api.constrains('document_file')
    def _check_file(self):
        self.ensure_one()
        if self.document_name and not self.document_name.endswith('.pdf'):
            raise ValidationError("Cannot upload file different from .pdf file")

    def add_document(self):
        return True

    def action_show_document(self):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        attachment_id = self.env['ir.attachment'].sudo().search([('res_model', '=', 'hr.employee.travel'),
                                                                 ('res_field', '=', 'document_file'),
                                                                 ('res_id', 'in', [self.id])], limit=1)
        action = {
            'type': 'ir.actions.act_url',
            'url': '{}/web/content/{}'.format(base_url, attachment_id.id),
            'target': 'new'
        } if attachment_id else False
        return action
