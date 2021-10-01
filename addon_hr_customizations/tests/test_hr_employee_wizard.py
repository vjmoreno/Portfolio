# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from odoo import fields
from odoo.tests import common, tagged
import unittest


@tagged('standard','post_install', '-at_install','create_employee_wizard')
class TestHREmployeeWizard(common.TransactionCase):
    def setUp(self):
        super(TestHREmployeeWizard, self).setUp()
        print("Setup Employee Data Started . . .")
        self.Contact = self.env['res.partner']
        self.contact_0001 = self.Contact.create(
            {
                'name': 'Contact 00001',
                'country_id': self.env['res.country'].search([('name','=','Serbia')],limit=1).id,
                'city': 'Nis',
                'email': 'test0001@example.com'
            }
        )

        self.User = self.env['res.users']

        self.group_employee_id = self.env.ref('base.group_user').id
        self.group_hr_manager = self.env.ref('hr.group_hr_manager').id
        self.group_system_id = self.env.ref('base.group_system').id

        self.user_100 = self.User.with_context({'no_reset_password': True}).create({
            'name': 'Test User 100',
            'login': 'user100',
            'email': 'marko@nanoramic.com',
            'tz': 'Europe/Belgrade',
            'groups_id': [(6, 0, [
                self.group_employee_id,
                self.group_hr_manager,
                self.group_system_id])]
        })


    # Test Create Employee with same email
    def test_create_employee_existing_email(self):
        print("Test Create Employee from wizard started . . .")
        self.first_name = 'Test0001 Name'
        self.last_name = 'Test0001 LastName'
        self.job_title = 'QA'
        self.department_id = self.env['hr.department'].search([],limit=1).id
        self.company_id = self.env['res.company'].search([], limit=1).id
        self.relationships = self.env.ref('addon_hr_customizations.employee_relationship_1').id
        self.parent_id = self.env['hr.employee'].search([], limit=1).id
        self.personal_email = self.contact_0001.email

        rec_wiz = self.env['hr.employee.create.wizard'].create({
            'first_name': self.first_name,
            'last_name': self.last_name,
            'job_title': self.job_title,
            'department_id': self.department_id,
            'company_id': self.company_id,
            'relationships': self.relationships,
            'parent_id': self.parent_id,
            'personal_email': self.personal_email,
            'work_location': 'from_home'
        })

        self.assertEqual(rec_wiz.first_name, self.first_name)
        self.assertEqual(rec_wiz.last_name, self.last_name)
        self.assertEqual(rec_wiz.job_title, self.job_title)
        self.assertEqual(rec_wiz.department_id.id, self.department_id)
        self.assertEqual(rec_wiz.company_id.id, self.company_id)
        self.assertEqual(rec_wiz.parent_id.id, self.parent_id)
        self.assertEqual(rec_wiz.personal_email, self.personal_email)

        rec_wiz_form = common.Form(rec_wiz)
        rec_wiz_form.personal_email = self.personal_email

        # Testing On Change Values
        self.assertEqual(rec_wiz_form.country_id.id, self.contact_0001.country_id.id)
        self.assertEqual(rec_wiz_form.city, self.contact_0001.city)
        rec_wiz = rec_wiz_form.save()

        employee = rec_wiz.create_employee()
        employee = self.env['hr.employee'].browse(employee['res_id'])
        self.assertEqual(rec_wiz.contact_id.id, employee.address_home_id.id)


        print("Test Create Employee from wizard done!")



if __name__ == '__main__':
    unittest.main()