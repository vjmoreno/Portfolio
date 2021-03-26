# -*- coding: utf-8 -*-
{
	'name': "Apiux background form",
	'description': '',
	'author': "Vicente Moreno",
	'data': ['views/apiux_background_form_view.xml',
			'views/apiux_onboard_view.xml',
			'security/user_groups.xml',
			'security/ir.model.access.csv'],
	'depends': ['apiux_hr_r', 
			'apiux_onboard', 
			'hr', 
			'base', 
			'hr_recruitment', 
			'apiux_hr_job'],
	'application': True
}