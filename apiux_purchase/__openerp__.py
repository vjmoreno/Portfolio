# -*- coding: utf-8 -*-
{
    'name': "apiux_purchase",
    'summary': """
       Set de customizaciones para las solicitudes de compra y facturas de APIUX
    """,
    'description': """
    """,
    'author': "Opensolve & Vicente Moreno",
    'website': "http://www.opensolve.org",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'version': '0.2',
    # any module necessary for this one to work correctly
    'depends': [
        'purchase',
        'account', 
        'purchase', 
        'account_cost_center',
        'mail',
        'email_template',
        'hr',
        'base_setup',
        'apiux_account_payment'
    ],
    # always loaded
    'data': [
        'views/purchase_view.xml',
        'views/report_purchaseorder.xml',
        'views/purchase_order_workflow.xml',
        'security/user_groups.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
}