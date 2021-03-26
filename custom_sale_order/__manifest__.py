# -*- coding: utf-8 -*-
{
	'name': 'Custom Sale',
	'version': '1',
	'author': 'Vicente Moreno',
	'depends': ['base', 'account', 'sale'],
	'data': ['./views/sale_order.xml', './views/res_partner.xml'],
	'description': """
					Sales Orders:
					
					- Inc. GST price will update the ex. GST and total prices.
					- Customer's displayed names will be: Customer ID  + Customer name +  ZIP code
					- Delivery Addresses will show only 'shipping addresses'
					
					Contacts:
					- Each of the addresses under the Contacts & Addresses tab will show the address instead of the name.
	""",
	'installable': True,
}