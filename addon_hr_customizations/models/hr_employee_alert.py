# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.modules.module import get_module_resource
from datetime import datetime
import base64
import ast


class EmployeeAlert(models.Model):

    _name = 'hr.employee.alert'
    _description = "Alert"
    _order = 'id'

    name = fields.Char(string='Alert', required=True)
    employee = fields.Many2one('hr.employee', string='Employee')
    created_on = fields.Date(string='Created on', default=fields.Date.today())
    string_date = fields.Char(string='strdate', compute='_compute_string_date')
    image_128 = fields.Image(related='employee.image_128', string='Employee Image 128')
    employee_name = fields.Char(related='employee.name', string='Employee Name', store=True)
    skipped_alerts = fields.One2many('hr.employee.alert.skip', 'alert_type', string='Skipped Alerts')
    hide_button = fields.Boolean(string='hide run alerts', default=False)
    color = fields.Integer()

    def raise_employee_alert(self):
        for record in self.env['hr.employee.alert.rule'].search([]):
            filtered_employees = self.env['hr.employee'].search(ast.literal_eval(record.rule))
            reverse_filtered_employees = self.env['hr.employee'].search([('id', 'not in', filtered_employees.ids)])
            for employee in self.env['hr.employee'].search([]):
                if employee.state != 'active':
                    self.env['hr.employee.alert'].search([('name', '=', record.alert), ('employee', '=', employee.id)]).sudo().unlink()
            for employee in filtered_employees:
                if bool(self.env['hr.employee.alert'].search([('name', '=', record.alert), ('employee', '=', employee.id)])) == False and bool(self.env['hr.employee.alert.skip'].search([('name', '=', record.alert), ('employee', '=', employee.id)])) == False and record.rule_active == True and employee.state == 'active' :
                    self.env['hr.employee.alert'].create({
                        'name': record.alert,
                        'employee': employee.id,
                        'created_on': fields.Date.today()
                    })
            for employee in reverse_filtered_employees:
                self.env['hr.employee.alert'].search([('name', '=', record.alert), ('employee', '=', employee.id)]).sudo().unlink()
    
    def trigger_raise_employee_alert(self):
        result = self.env.ref('addon_hr_customizations.ir_cron_raise_employee_alerts').method_direct_trigger()
        return result
    
    def skip_employee(self):
        for record in self:
            self.env['hr.employee.alert.skip'].create({
                'name': record.name,
                'alert_type': record.id,
                'employee': record.employee.id,
            })
            record.unlink()
        return {'type': 'ir.actions.act_view_reload'}

    def delete_skip_employee(self):
        for record in self:
            record.unlink()
        return {'type': 'ir.actions.act_view_reload'}
    
    @api.depends('created_on')
    def _compute_string_date(self):
        for alert in self:
            alert.string_date = str(alert.created_on.strftime("%d-%b-%Y"))
    
    def employee_new_tab(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        menu_id = self.env.ref('hr.menu_hr_root').id
        action_id = self.env.ref('hr.open_view_employee_list_my').id
        record_url = base_url +"/web#id="+ str(self.employee.id) +"&action="+ str(action_id) +"&model=hr.employee&view_type=form&cids=&menu_id="+ str(menu_id)
        client_action = {
            'type': 'ir.actions.act_url',
            'name': "Employee",
            'target': 'new',
            'url': record_url,
        }
        return client_action


class EmployeeSkipAlert(models.Model):

    _name = 'hr.employee.alert.skip'
    _description = "Skip Alert"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id'

    name = fields.Char(string='Name', required=True)
    alert_type = fields.Many2one('hr.employee.alert', string='Alert')
    employee = fields.Many2one('hr.employee', string='Employee')
    created_on = fields.Date(string='Created on', default=fields.Date.today())
    created_by = fields.Many2one('res.users', string='Created by', default=lambda self: self.env.user)


class EmployeeAlertRule(models.Model):

    _name = 'hr.employee.alert.rule'
    _description = "Alert Rule"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id'

    name = fields.Char(string='Name', required=True)
    alert = fields.Char(string='Alert', required=True)
    rule = fields.Text(string='Rule')
    rule_active = fields.Boolean(string='Active', default=True)
    color = fields.Integer()


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    alerts = fields.One2many('hr.employee.alert', 'employee', string='Alerts')
    skipped_alerts = fields.One2many('hr.employee.alert.skip', 'employee', string='Skipped Alerts')
    employee_alerts_count = fields.Integer(string="Alerts", compute='_compute_employee_alerts_count', store=True)
    hr_default_image = fields.Image("Hr Default", compute='_compute_hr_default_image', compute_sudo=True)
    has_default = fields.Boolean(string='Has Default Image', compute='_compute_has_default_image', store=True)
    
    @api.depends('alerts')
    def _compute_employee_alerts_count(self):
        for employee in self:
            employee.employee_alerts_count = len(employee.alerts)
    
    @api.depends('name')
    def _compute_hr_default_image(self):
        image_path = get_module_resource('addon_hr_customizations', 'static/src/img', 'default_image.png')
        for employee in self:
            employee.hr_default_image = base64.b64encode(open(image_path, 'rb').read())
    
    @api.depends('image_1920')
    def _compute_has_default_image(self):
        for record in self:
            if str(record.image_1920) == str(record.hr_default_image):
                record.has_default = True
            else: 
                record.has_default = False
    
    def get_employee_alerts(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Alerts',
            'view_mode': 'kanban,tree',
            'res_model': 'hr.employee.alert',
            'domain': [('employee', '=', self.id)],
            'context': "{ 'group_by': 'name'}"
        }
