# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Debranding and Branding (Backend + Frontend)',
    'author':   'IRSIS Corp',
    'website':  'https://www.irsis.ph',
    'license':  'OPL-1',
    'version': '1.0',
    'category': 'Extra Tools',
    'sequence': 1,
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/res_company_data.xml',
        'data/res_groups.xml',
        'data/mailbot_data.xml',
        'views/web_debranding_view.xml',
        'views/app_theme_config_settings_view.xml',
        'views/ir_model_view.xml',
        'views/res_users_views.xml',
        'views/ir_module_views.xml',
        'views/web_template_view.xml'

    ],
    'qweb': [
        'static/src/xml/dashboard.xml',
        'static/src/xml/customize_user_menu.xml',

    ],
    'images': [
        'static/description/main_screen.jpg'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'pre_init_hook': 'pre_init_hook',
}