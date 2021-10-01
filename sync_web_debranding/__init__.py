# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from . import models
from . import controllers


from odoo import api, SUPERUSER_ID


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    company_image = False
    datas = env['mail.template'].search([])
    for data in datas:
        data.write({'name': data.name.replace('Odoo', ''),
                    'body_html': data.body_html.replace('Powered by', '').replace('Odoo', '') if isinstance(data.body_html, str) else data.body_html,
                    'subject': data.subject.replace('Odoo', '') if isinstance(data.subject, str) else data.subject
                    })
        if isinstance(data.body_html, str) and data.body_html.find('/logo.png?company=${object.company_id.id}'):
            data.write({
                'body_html': data.body_html.replace('/logo.png?company=${object.company_id.id}', '/web/image?model=res.company&field=logo&id=${object.company_id.id}')
                })
