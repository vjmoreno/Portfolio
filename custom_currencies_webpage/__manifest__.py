# -*- coding: utf-8 -*-
{
	'name': 'Backend currencies',
	'version': '1',
	'author': 'Vicente Moreno',
	'depends': ['product',
				'base',
				'base_setup',
				'sale',
				'purchase'],
	'description':	"""
					This module does two things:\n
					1) Add the website prices to products views  (kanban and form views)\n
					2) It gives the user the possibility to choose if they want to keep the same prices for all companies.\n
					The new option can be found in:\n
					settings -> \n
					general settings ->\n 
					Multi - companies -> \n
					Multi - company - same rates.\n
					
					""",
	'data': ['views/product_template_views.xml',
			 'views/res_config_settings.xml',
	],
	'installable': True,
}