# -*- coding: utf-8 -*-
{
    'name': 'Red Tags',
    'Description': 'Odoo app to manage Red Tags in order to better manage equipment usage, storage, and disposal.',
    'version': '1',
    'depends': ['addon_editor_js', 'mail', 'addon_hide_send_email_button', 'addon_nanoramic_new_equipment',
                'addon_restful'],
    'author': 'Nanoramic Laboratories',
    'data': ['security/security.xml',
             'security/ir.model.access.csv',
             'views/red_tag_item_type_views.xml',
             'views/red_tag_reason_views.xml',
             'views/red_tag_transition_activity_views.xml',
             'views/red_tag_views.xml',
             'views/menu_items.xml',
             'data/red_tag_item_types.xml',
             'data/red_tag_reasons.xml'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
