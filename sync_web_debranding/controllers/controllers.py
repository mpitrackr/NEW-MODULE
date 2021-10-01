# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import json
import odoo
import os
import sys
import jinja2
from odoo import http, tools
from odoo.addons.web.controllers.main import Database
from odoo.addons.web.controllers import main
from odoo.http import request

if hasattr(sys, 'frozen'):
    # When running on compiled windows binary, we don't have access to package loader.
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('odoo.addons.sync_web_debranding', "views")
env = main.jinja2.Environment(loader=loader, autoescape=True)
env.filters["json"] = json.dumps
db_monodb = http.db_monodb


class OdooDebrand(Database):
    # Render the Database management html page
    def _render_template(self, **d):
        d.setdefault('manage', True)
        d['insecure'] = odoo.tools.config.verify_admin_password('admin')
        d['list_db'] = odoo.tools.config['list_db']
        d['langs'] = odoo.service.db.exp_list_lang()
        d['countries'] = odoo.service.db.exp_list_countries()
        d['pattern'] = main.DBNAME_PATTERN
        # databases list
        d['databases'] = []
        try:
            d['databases'] = http.db_list()
            d['incompatible_databases'] = odoo.service.db.list_db_incompatible(d['databases'])
        except odoo.exceptions.AccessDenied:
            monodb = db_monodb()
            if monodb:
                d['databases'] = [monodb]
        try:
            d['company_name'] = request.env['ir.config_parameter'].sudo().get_param('sync_app_system_name') or ''
            d['favicon'] = request.env['ir.config_parameter'].sudo().get_param('sync_app_company_fevicon') or ''
            d['company_logo_url'] = '/web/binary/company_logo'        
            
            return env.get_template("database_manager_extend.html").render(d)
        except Exception as e:
            print("An error has occured: {}".format(e))
            d['company_name'] = ''
            d['favicon'] = ''
            d['company_logo_url'] = ''
            return env.get_template("database_manager.html").render(d)
