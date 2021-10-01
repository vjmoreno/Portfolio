# -*- coding: utf-8 -*-
{
    'name': "Slack Integration for Red Tags",

    'summary': "Slack Integration for Red Tags",
    'description': "Slack Integration for Red Tags",
    'author': "Nanoramic",
    'depends': ['addon_restful', 'base', 'mail', 'red_tags', 'slack'],
    'data': [
        'data/slack_events.xml',
        'data/slack_defaults.xml',
        'views/res_config_settings.xml',
    ],
}
