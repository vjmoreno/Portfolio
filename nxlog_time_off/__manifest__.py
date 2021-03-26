# -*- coding: utf-8 -*-
{
    'name': 'NXLog - Time off',
    'summary': """Time off customizations""",
    'description': """
                    This module includes modifications principally modifications to the time off module.,
                    but also content related to other issues. Here is the list of Gitlab issues related to
                    this module:\n
                   1) The module creates an ir_model_data record:
                   https://gitlab.com/nxlog/openhrms/-/issues/2#note_487221969\n
                   2) Creates 2 different reposts described here:
                   https://gitlab.com/nxlog/openhrms/-/issues/6\n
                   3) Creates the following view:
                   https://gitlab.com/nxlog/openhrms/-/issues/7#note_491230435\n"""
                   ,
    'category': 'Generic Modules/Human Resources',
    'author': 'NXLog',
    'company': 'NXLog',
    'depends': ['hr', 'hr_holidays', 'hr_resignation'],
    'demo': [],
    'data': ['reports/time_off_report.xml',
             'views/hr_employee_views.xml',
             'data/ir_model_data.xml'],
    'installable': True,
    'auto_install': False,
    'application': False,
}
