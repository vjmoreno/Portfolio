# -*- coding: utf-8 -*-
{
    'name': 'QR codes',
    'Description': 'App to link qr codes to objects.',
    'version': '1',
    'depends': ['addon_equipment_movement', 'addon_restful', 'maintenance', 'mrp_maintenance'],
    'author': 'Nanoramic Laboratories',
    'data': ['views/qr_code_views.xml',
             'views/maintenance_equipment_views.xml',
             'views/menu_items.xml',
             'wizards/qr_code_wizard_views.xml',
             'security/ir.model.access.csv',
             'views/assets_backend.xml'],
    'qweb': ['static/src/xml/link_button.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
