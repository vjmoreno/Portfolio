# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install', 'addon_nanoramic_onboarding')
class TestEmploymentPeriod(TransactionCase):

    def setUp(self):
        super(TestEmploymentPeriod, self).setUp()

        self.partner = self.env['res.partner'].create({'name': 'Jean Dupont', 'email': 'jean.dupont@nanoramic.com'})
        self.employee = self.env['hr.employee'].create({
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'work_email': 'jean.dupont@nanoramic.com',
            'address_home_id': self.partner.id,
            'job_title': 'Odoo Developer',
            'start_date': '2021-01-01',
            'mobile_phone': '0123456789'
        })
        self.relationship = self.env['hr.employee.relationships'].search([], limit=1)
        self.company = self.env.user.company_id

    def test_001_create_employment_period(self):
        """
            1. Create an employment period for the employee
            2. Create an open employment period
        """
        employment_period_obj = self.env['employment.period']
        values = {
            'start_date': '2021-08-01',
            'termination_date': '2021-08-31',
            'termination_reason': 'The is a termination reason',
            'relationship_id': self.relationship.id,
            'company_id': self.company.id,
            'employee_id': self.employee.id
        }
        employment_period_obj.create(values)
        self.assertEquals(len(self.employee.employment_period_ids), 1)
        values = {
            'start_date': '2021-08-01',
            'relationship_id': self.relationship.id,
            'company_id': self.company.id,
            'employee_id': self.employee.id
        }
        employment_period_obj.create(values)
        self.assertEquals(len(self.employee.employment_period_ids), 2)

    def test_002_raise_overlapping_employment_period(self):
        """
            1. Create an employment period
            2. Create another employment period that overlap with the first one
            3. Check raise
        """
        employment_period_obj = self.env['employment.period']
        values = {
            'start_date': '2021-08-01',
            'termination_date': '2021-08-31',
            'termination_reason': 'The is a termination reason',
            'relationship_id': self.relationship.id,
            'company_id': self.company.id,
            'employee_id': self.employee.id
        }
        employment_period_obj.create(values)
        self.assertEquals(len(self.employee.employment_period_ids), 1)
        values = {
            'start_date': '2021-08-15',
            'termination_date': '2021-09-30',
            'termination_reason': 'The is a termination reason',
            'relationship_id': self.relationship.id,
            'company_id': self.company.id,
            'employee_id': self.employee.id
        }
        with self.assertRaises(ValidationError):
            employment_period_obj.create(values)

    def test_003_raise_two_open_employment_period(self):
        """
            1. Create an open employment period
            2. Create another open employment period
            3. Check raise
        """
        employment_period_obj = self.env['employment.period']
        values = {
            'start_date': '2021-08-01',
            'relationship_id': self.relationship.id,
            'company_id': self.company.id,
            'employee_id': self.employee.id
        }
        employment_period_obj.create(values)
        self.assertEquals(len(self.employee.employment_period_ids), 1)
        values = {
            'start_date': '2021-08-15',
            'relationship_id': self.relationship.id,
            'company_id': self.company.id,
            'employee_id': self.employee.id
        }
        with self.assertRaises(ValidationError):
            employment_period_obj.create(values)

    def test_004_raise_start_date_gt_termination_date(self):
        """
            1. Create an employment period with start date greater than termination date
            3. Check raise
        """
        employment_period_obj = self.env['employment.period']
        values = {
            'start_date': '2021-08-31',
            'termination_date': '2021-08-01',
            'termination_reason': 'The is a termination reason',
            'relationship_id': self.relationship.id,
            'company_id': self.company.id,
            'employee_id': self.employee.id
        }
        with self.assertRaises(ValidationError):
            employment_period_obj.create(values)
