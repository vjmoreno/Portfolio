# -*- coding: utf-8 -*-
{
    'name': 'Personal Equipment',
    'Description': 'App to track personal equipment provided to employees.',
    'version': '1',
    'depends': ["equipment_allocations"],
    'author': 'Nanoramic Laboratories',
    'data': ['views/allocation_request_views.xml',
             'views/menu_items.xml',
             'views/hr_employee_views.xml',
             'wizards/return_personal_equipment_wizard_views.xml',
             'security/ir.model.access.csv'],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
