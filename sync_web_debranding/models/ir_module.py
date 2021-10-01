# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _

class ModuleCategory(models.Model):
    _inherit = "ir.module.category"

    hide_website_author = fields.Selection([('yes', 'Yes'), ('no', 'No')], default="no", compute="_get_value")

    def _get_value(self):
        value = self.env['res.config.settings'].get_values()
        if value.get('group_show_author_in_apps'):
            self.hide_website_author = "yes"
        else:
            self.hide_website_author = "no"

class Module(models.Model):
    _inherit = "ir.module.module"

    hide_website_author = fields.Selection(related='category_id.hide_website_author')