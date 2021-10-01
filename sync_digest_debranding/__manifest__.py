# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Debranding Digest',
    'author':   'IRSIS Corp',
    'website':  'https://www.irsis.ph',
    'license':  'OPL-1',
    'version': '1.0',
    'category': 'Extra Tools',
    'sequence': 1,
    'depends': ['sync_web_debranding', 'digest'],
    'data': [
        'data/digest_data.xml',
    ],
    'qweb': [
    ],
    'images': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}