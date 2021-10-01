# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import re
from odoo import api, models, tools

# Change Tour(planner Footer)
def debrand_documentation_links(source, new_documentation_website):
    if new_documentation_website and source:
        return re.sub(r'https://www.odoo.com/documentation/',
                      new_documentation_website + 'documentation/',
                      source, flags=re.IGNORECASE)


def debrand_links(source, new_website):
    if new_website:
        return re.sub(r'\bwww.odoo.com\b', new_website, source, flags=re.IGNORECASE)


def debrand(env, source, is_code=False):
    if not source or not re.search(r'\bodoo\b', source, re.IGNORECASE):
        return source

    new_name = env['ir.config_parameter'].sudo().get_param('sync_app_system_title')
    new_website = env['ir.config_parameter'].sudo().get_param('sync_app_system_url')
    new_documentation_website = env['ir.config_parameter'].sudo().get_param('sync_app_documentation_url')

    source = debrand_documentation_links(source, new_documentation_website)
    if source and new_website:
        source = debrand_links(source, new_website)
        source = re.sub(r'\b(?<!\.)odoo(?!\.\S|\s?=|\w|\[)\b', new_name, source, flags=re.IGNORECASE)
    return source


def debrand_bytes(env, source):
    return bytes(debrand(env, source.decode('utf-8')), 'utf-8')


# Warning model Text odoo replace
class IrTranslation(models.Model):
    _inherit = 'ir.translation'

    @api.model
    def _debrand_dict(self, res):
        for k in res:
            res[k] = self._debrand(res[k])
        return res

    @api.model
    def _debrand(self, source):
        return debrand(self.env, source)

    @tools.ormcache('name', 'types', 'lang', 'source', 'res_id')
    def __get_source(self, name, types, lang, source, res_id):
        res = super(IrTranslation, self).__get_source(name, types, lang, source, res_id)
        return self._debrand(res)

    @api.model
    @tools.ormcache_context('model_name', keys=('lang',))
    def get_field_string(self, model_name):
        res = super(IrTranslation, self).get_field_string(model_name)
        return self._debrand_dict(res)

    @api.model
    @tools.ormcache_context('model_name', keys=('lang',))
    def get_field_help(self, model_name):
        res = super(IrTranslation, self).get_field_help(model_name)
        return self._debrand_dict(res)
