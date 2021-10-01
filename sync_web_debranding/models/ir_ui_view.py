# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, api
from .ir_translation import debrand

class View(models.Model):
    _inherit = 'ir.ui.view'

    # all view
    def read_combined(self, fields=None):
        res = super(View, self).read_combined(fields=fields)
        res['arch'] = debrand(self.env, res['arch'], is_code=True)
        return res

    @api.model
    def render_template(self, template, values=None, engine='ir.qweb'):
        if template in ['web.login', 'web.webclient_bootstrap']:
            if not values:
                values = {}
            values["title"] = self.env['ir.config_parameter'].sudo().get_param("sync_app_system_name", "yourcompany")
        return super(View, self).render_template(template, values=values, engine=engine)
