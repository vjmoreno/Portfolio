# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrEmployeeCitizenshipDocument(models.Model):

    _name = 'hr.employee.citizenship'
    _description = 'Employee Citizenship Documents'

    employee_id = fields.Many2one('hr.employee', required=True)
    citizenship = fields.Char(string="Citizenship", required=True)
    passport_number = fields.Char(string="Passport Number", required=True)
    country_id = fields.Many2one('res.country', string="Issuing Country", required=True)
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
        attachment_id = self.env['ir.attachment'].sudo().search([('res_model', '=', 'hr.employee.citizenship'),
                                                                 ('res_field', '=', 'document_file'),
                                                                 ('res_id', 'in', [self.id])], limit=1)
        action = {
            'type': 'ir.actions.act_url',
            'url': '{}/web/content/{}'.format(base_url, attachment_id.id),
            'target': 'new'
        } if attachment_id else False
        return action
