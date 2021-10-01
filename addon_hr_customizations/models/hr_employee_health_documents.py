# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrEmployeeHealthDocument(models.Model):

    _name = 'hr.employee.health'
    _description = 'Employee Health Documents'

    employee_id = fields.Many2one('hr.employee', required=True)
    name = fields.Char(required=True)
    issued_by = fields.Char(required=True)
    issued_date = fields.Date(required=True)
    expiry_date = fields.Date(required=True)
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
        attachment_id = self.env['ir.attachment'].sudo().search([('res_model', '=', 'hr.employee.health'),
                                                                 ('res_field', '=', 'document_file'),
                                                                 ('res_id', 'in', [self.id])], limit=1)
        action = {
            'type': 'ir.actions.act_url',
            'url': '{}/web/content/{}'.format(base_url, attachment_id.id),
            'target': 'new'
        } if attachment_id else False
        return action
