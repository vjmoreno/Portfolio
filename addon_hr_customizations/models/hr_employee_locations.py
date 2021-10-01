# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree


class ResCountryEmployee(models.Model):
    _inherit = 'res.country'

    employees = fields.One2many('hr.employee', 'country_work_location', string='Employees',
                                domain=['|', ('state', '=', 'onboarding'), ('state', '=', 'active')])
    employee_count = fields.Integer(compute='_compute_employee_count', string='Employees count')
    color = fields.Integer()
    country = fields.Many2one('res.country', compute='_compute_employee_count', store=True)
    department_id = fields.Many2many('hr.department', 'rel_department_res_county', compute='_compute_employee_count',
                                     store=True)

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        res = super(ResCountryEmployee, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                              submenu=submenu)

        query_department = '''

        SELECT  CASE
    WHEN parent_id Is Null THEN id
    ELSE parent_id
    END AS department
FROM hr_department ;'''
        self.env.cr.execute(query_department)
        result_department = self.env.cr.fetchall()

        doc = etree.XML(res['arch'])
        if not result_department:
            list_department = []
        else:
            list_department = [x[0] for x in result_department]

        for node in doc.xpath("//searchpanel/field[@name='department_id']"):
            node.set('domain', "[('id','in',%s)]" % list_department)

        res['arch'] = etree.tostring(doc)
        return res

    def _get_employees(self):
        for country in self:
            matching_employees = []
            for employee in self.env['hr.employee'].search([('country_work_location', '=', country.id)]):
                matching_employees.append(employee.id)
            country.write({'employees': [(6, 0, matching_employees)]})

    def _compute_employee_count(self):
        for country in self.env['res.country'].search([]):
            country.employee_count = len(country.employees)
            if country.employee_count > 0:
                country.country = country.id
                department_list = []
                for rec in country.employees:
                    if rec.department_id.id not in department_list:
                        if rec.department_id.parent_id:
                            department_list.append(rec.department_id.parent_id.id)
                        else:
                            department_list.append(rec.department_id.id)
                country.department_id = department_list
            if not country.employee_count:
                country.country = False

    @api.model
    def country_blank_state(self):
        Countries = self.env['res.country'].search([])
        for country in Countries:
            if bool(self.env['res.country.state'].search(
                    [('name', '=', 'Blank'), ('country_id', '=', country.id)])) is False:
                self.env['res.country.state'].create({
                    'name': 'Blank',
                    'code': '00',
                    'country_id': country.id,
                })

    def get_department(self, k):
        employee_len = self.env['hr.employee'].search_count(
            [('user_id', '!=', False), ('department_id', '=', self.id), ('state', '=', 'active')])
        return employee_len, k


class ResStateEmployee(models.Model):
    _inherit = 'res.country.state'
    _order = 'country_id'

    employees = fields.One2many('hr.employee', 'state_work_location', string='Employees',
                                domain=['|', ('state', '=', 'onboarding'), ('state', '=', 'active')])
    employee_count = fields.Integer(compute='_compute_employee_count', string='Employees count')
    country_name = fields.Char(related='country_id.name', string="Location")
    flag = fields.Binary(related='country_id.image', string="Flag")
    color = fields.Integer()
    state = fields.Many2one('res.country.state', compute='_compute_employee_count', store=True)
    country = fields.Many2one('res.country', compute='_compute_employee_count', store=True)
    department_id = fields.Many2many('hr.department', 'rel_department_county', compute='_compute_employee_count',
                                     store=True)

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        res = super(ResStateEmployee, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                            submenu=submenu)

        query_department = '''
SELECT  CASE
    WHEN parent_id Is Null THEN id
    ELSE parent_id
    END AS department
FROM hr_department;'''
        self.env.cr.execute(query_department)
        result_department = self.env.cr.fetchall()
        doc = etree.XML(res['arch'])
        if not result_department:
            list_department = []
        else:
            list_department = [x[0] for x in result_department]

        for node in doc.xpath("//searchpanel/field[@name='department_id']"):
            node.set('domain', "[('id','in',%s)]" % list_department)

        res['arch'] = etree.tostring(doc)
        return res

    def _get_employees(self):
        for state in self:
            matching_employees = []
            for employee in self.env['hr.employee'].search([('state_work_location', '=', state.id)]):
                matching_employees.append(employee.id)
            state.write({'employees': [(6, 0, matching_employees)]})

    def _compute_employee_count(self):
        for state in self:
            state.employee_count = len(state.employees)
            if state.employee_count > 0:
                state.state = state.id
                state.country = state.country_id.id
                department_list = []
                for rec in state.employees:
                    if rec.department_id.id not in department_list:
                        if rec.department_id.parent_id:
                            department_list.append(rec.department_id.parent_id.id)
                        else:
                            department_list.append(rec.department_id.id)

                state.department_id = department_list
            else:
                state.state = False
                state.country = False
