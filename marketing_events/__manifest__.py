# -*- coding: utf-8 -*-
{
    'name': 'Marketing Events',
    'Description': 'Odoo app to manage the marketing events',
    'version': '1',
    'depends': ['mail', 'addon_hide_send_email_button',],
    'author': 'Nanoramic Laboratories',
    'data': ['security/security.xml',
             'security/ir.model.access.csv',
             'views/menu_items.xml',
             'views/marketing_event_views.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
