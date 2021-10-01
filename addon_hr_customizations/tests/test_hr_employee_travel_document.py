# -*- coding: utf-8 -*-

import base64
from odoo.tests.common import SingleTransactionCase, tagged, Form
from odoo.exceptions import ValidationError
from datetime import datetime


@tagged('post_install', '-at_install', 'addon_hr_customizations', 'hr_employee_travel_document')
class TestHrEmploymentTravelDocument(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestHrEmploymentTravelDocument, cls).setUpClass()
        hr_employee = cls.env['hr.employee']
        cls.hr_employee_01 = hr_employee.create({
            'first_name': 'EmployeeFirstName01',
            'last_name': 'EmployeeLastName01',
            'job_title': 'EmployeeJobTitle01',
            'work_email': 'employee.mail01@testmail.com',
            'country_id': 1,
            'work_location': 'from_home',
        })

    def test_hr_employee_travel_document_001(self):
        """ Verify I can add a travel document to an employee
        """
        add_travel_document = self.hr_employee_01.add_travel_document()
        wizard_ref_id = 'addon_hr_customizations.hr_employee_travel_documents_form_view_wizard'
        wizard_id = self.env.ref(wizard_ref_id).id
        self.assertEqual(add_travel_document.get('view_mode'), 'form')
        self.assertEqual(add_travel_document.get('res_model'), 'hr.employee.travel')
        self.assertEqual(add_travel_document.get('views', [[0]])[0][0], wizard_id)
        employee_travel_form = Form(
            self.env['hr.employee.travel'].with_context(
                {'default_employee_id': self.hr_employee_01.id}),
            wizard_ref_id)
        employee_travel_form.document_type = 'passport'
        employee_travel_form.document_number = '123'
        employee_travel_form.country_id = self.env['res.country'].search([('name', '=', 'United States')], limit=1)
        employee_travel_form.citizenship = 'American'
        employee_travel_form.issued_date = datetime.now()
        employee_travel_form.expiry_date = datetime.now()
        test_file = base64.b64encode(bytes("TEST PDF", 'utf-8'))
        employee_travel_form.document_file = test_file
        travel_document_id = employee_travel_form.save()
        self.assertTrue(travel_document_id)

    def test_hr_employee_travel_document_002(self):
        """ Verify I can remove a travel document from the employee form view
        """
        self.assertEqual(len(self.hr_employee_01.travel_document_ids), 1)
        employee_travel_form = Form(
            self.env['hr.employee.travel'].with_context(
                {'default_employee_id': self.hr_employee_01.id}),
            'addon_hr_customizations.hr_employee_travel_documents_form_view_wizard')
        employee_travel_form.document_type = 'passport'
        employee_travel_form.document_number = '123'
        employee_travel_form.country_id = self.env['res.country'].search([('name', '=', 'United States')], limit=1)
        employee_travel_form.citizenship = 'American'
        employee_travel_form.issued_date = datetime.now()
        employee_travel_form.expiry_date = datetime.now()
        test_file = base64.b64encode(bytes("TEST PDF 2", 'utf-8'))
        employee_travel_form.document_file = test_file
        employee_travel_form.save()
        self.assertEqual(len(self.hr_employee_01.travel_document_ids), 2)
        employee_form = Form(self.hr_employee_01)
        employee_form.travel_document_ids.remove(0)
        employee_form.save()
        self.assertEqual(len(self.hr_employee_01.travel_document_ids), 1)

    def test_hr_employee_travel_document_003(self):
        """ Verify I can edit an employee's travel document details
        """
        usa_country = self.env['res.country'].search([('name', '=', 'United States')], limit=1)
        bolivia_country = self.env['res.country'].search([('name', '=', 'Bolivia')], limit=1)
        employee_travel_form = Form(
            self.env['hr.employee.travel'].with_context(
                {'default_employee_id': self.hr_employee_01.id}),
            'addon_hr_customizations.hr_employee_travel_documents_form_view_wizard')
        employee_travel_form.document_type = 'passport'
        employee_travel_form.document_number = '123'
        employee_travel_form.country_id = usa_country
        employee_travel_form.citizenship = 'American'
        employee_travel_form.issued_date = datetime.now()
        employee_travel_form.expiry_date = datetime.now()
        test_file = base64.b64encode(bytes("TEST PDF 3", 'utf-8'))
        employee_travel_form.document_file = test_file
        employee_travel_form.save()
        document = self.hr_employee_01.travel_document_ids[1]
        self.assertEqual(document.document_type, 'passport')
        self.assertEqual(document.document_number, '123')
        self.assertEqual(document.country_id, usa_country)
        self.assertEqual(document.citizenship, 'American')
        with Form(self.hr_employee_01) as employee_form:
            with employee_form.travel_document_ids.edit(1) as document_line:
                document_line.document_type = 'id'
                document_line.document_number = '456'
                document_line.country_id = bolivia_country
                document_line.citizenship = 'Bolivian'
        self.assertEqual(document.document_type, 'id')
        self.assertEqual(document.document_number, '456')
        self.assertEqual(document.country_id, bolivia_country)
        self.assertEqual(document.citizenship, 'Bolivian')

    def test_hr_employee_travel_document_004(self):
        """ Verify I can open the travel document's PDF attachment in a new tab
        """
        document_00 = self.hr_employee_01.travel_document_ids[0]
        show_document_00 = document_00.action_show_document()
        self.assertEqual(show_document_00.get('type'), 'ir.actions.act_url')
        self.assertEqual(show_document_00.get('target'), 'new')
        self.assertTrue('/web/content/' in show_document_00.get('url', ''))
        document_01 = self.hr_employee_01.travel_document_ids[0]
        show_document_01 = document_01.action_show_document()
        self.assertEqual(show_document_01.get('type'), 'ir.actions.act_url')
        self.assertEqual(show_document_01.get('target'), 'new')
        self.assertTrue('/web/content/' in show_document_01.get('url', ''))

    def test_hr_employee_travel_document_005(self):
        """ Verify I can only upload PDF attachments to the travel document
        """
        document_00 = self.hr_employee_01.travel_document_ids[0]
        document_00.write({'document_name': 'test_document_00.any'})
        with self.assertRaises(ValidationError):
            document_00._check_file()
        document_00.write({'document_name': 'test_document_00.pdf'})
        self.assertEqual(document_00._check_file(), None)
        document_01 = self.hr_employee_01.travel_document_ids[1]
        document_01.write({'document_name': 'test_document_01.any'})
        with self.assertRaises(ValidationError):
            document_01._check_file()
        document_01.write({'document_name': 'test_document_01.pdf'})
        self.assertEqual(document_01._check_file(), None)
