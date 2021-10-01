# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployeeDocuments(models.Model):

    _inherit = 'hr.employee'

    documents = fields.One2many('documents.document', 'document_owner', string="Documents")
    employee_doc_count = fields.Integer(string="Documents", compute='_compute_employee_doc_count', store=True)
    
    @api.depends('documents')
    def _compute_employee_doc_count(self):
        for employee in self:
            employee.employee_doc_count = len(employee.documents)
    
    @api.model
    def get_employees_directory(self):
        Employees = self.env['hr.employee'].search([])
        Parent_folder = self.env['documents.folder'].search([('name', '=', 'HR')])
        Company = self.env['res.company'].search([('name', '=', 'Nanoramic Laboratories')])
        Officer_group = self.env['res.groups'].search([('name', '=', 'Officer'), ('category_id', '=', 'Employees')])
        Internal_user_group = self.env['res.groups'].search([('name', '=', 'Internal User'), ('category_id', '=', 'User types')])
        
        for employee in Employees:
            if bool(self.env['documents.folder'].search([('name', '=', employee.name)])) is False:
                self.env['documents.folder'].create({
                    'name': employee.name,
                    'parent_folder_id': Parent_folder.id,
                    'company_id': Company.id,
                    'group_ids': Officer_group,
                    'read_group_ids': Internal_user_group,
                    'folder_owner': employee.id,
                })
    
    def upload_to_folder(self): 
        from_form_view = self.env.context.get('from_form_view', False)
        folder_id = self.env['documents.folder'].search([('name', '=', self.name)]).id
        context = dict(self.env.context or {})        
        context.update({ 'from_form_view': from_form_view }) 
        context.update({ 'default_folder_id': folder_id }) 
        return  {
            'type': 'ir.actions.act_window',
            'name': 'documents form',
            'res_model': 'documents.document',
            'view_mode': 'form',
            'context': context,
            'target': 'new',
        }
    
    @api.model
    def create(self, vals):
        Employee = super(HrEmployeeDocuments, self).create(vals)
        Employee.get_employees_directory()
        return Employee


class FolderEmployee(models.Model):

    _inherit = 'documents.folder'

    folder_owner = fields.Many2one('hr.employee', string="My folder")


class DocumentEmployee(models.Model):

    _inherit = 'documents.document'

    document_owner = fields.Many2one('hr.employee', compute='_compute_document_owner', string="My documents", store=True)

    @api.depends('name')
    def _compute_document_owner(self):
        for record in self:
            record.write({'document_owner': self.env['hr.employee'].search([('name', '=', record.folder_id.name), ('id', '=', record.folder_id.folder_owner.id)]).id})
