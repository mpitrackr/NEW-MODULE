# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _

class AppThemeConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    _description = u"App Odoo Customize settings"

    # Rebranding
    sync_app_company_fevicon = fields.Binary('Company Fevicon')
    sync_app_system_name = fields.Char('System Name', help=u"Setup System Name,which replace Odoo", default="yourcompany", required=True)
    sync_app_system_title = fields.Char('System Title', help=u"Apply in Warning messages and No Record view",
                                        default="yourcompany", required=True)
    sync_app_system_url = fields.Char('System Website Url', default="http://www.yourcompany.com", required=True)

    # User Menu
    sync_app_show_debug = fields.Boolean('Show Quick Debug', help=u"When enable,everyone login can see the debug menu")
    sync_app_show_documentation = fields.Boolean('Show Documentation', help=u"When enable,User can visit user manual")
    sync_app_show_documentation_dev = fields.Boolean('Show Developer Documentation',
                                                     help=u"When enable,User can visit development documentation")
    sync_app_show_support = fields.Boolean('Show Support', help=u"When enable,User can vist your support site")
    sync_app_show_account = fields.Boolean('Show My Account', help=u"When enable,User can login to your website")

    # User Menu Content
    sync_app_documentation_url = fields.Char('Documentation Url')
    sync_app_documentation_dev_url = fields.Char('Developer Documentation Url')
    sync_app_support_url = fields.Char('Support Url')
    sync_app_account_title = fields.Char('Account Title')
    sync_app_account_url = fields.Char('Account Url')

    # Left Menu Footer
    sync_app_show_poweredby = fields.Boolean('Show Powered by', help=u"Uncheck to hide the Powered by text")

    # Install App View
    group_show_author_in_apps = fields.Boolean(string="Show Author and Website in Apps Dashboard",
                                               implied_group='sync_web_debranding.group_show_author_in_apps',
                                               help=u"Uncheck to Hide Author and Website in Apps Dashboard")

    # Easy to swich lang
    sync_app_show_lang = fields.Boolean('Show Quick Language Switcher',
                                        help=u"When enable,User can quick switch language in user menu")

    @api.model
    def get_values(self):
        ir_config = self.env['ir.config_parameter']
        res = super(AppThemeConfigSettings,self).get_values()

        # Rebranding
        sync_app_company_fevicon = ir_config.sudo().get_param('sync_app_company_fevicon')
        sync_app_system_name = ir_config.sudo().get_param('sync_app_system_name')
        sync_app_system_url = ir_config.sudo().get_param('sync_app_system_url')
        sync_app_system_title = ir_config.sudo().get_param('sync_app_system_title')

        # User Menu
        sync_app_show_debug = True if ir_config.sudo().get_param('sync_app_show_debug') == "True" else False
        sync_app_show_documentation = True if ir_config.sudo().get_param(
            'sync_app_show_documentation') == "True" else False
        sync_app_show_documentation_dev = True if ir_config.sudo().get_param(
            'sync_app_show_documentation_dev') == "True" else False
        sync_app_show_support = True if ir_config.sudo().get_param('sync_app_show_support') == "True" else False
        sync_app_show_account = True if ir_config.sudo().get_param('sync_app_show_account') == "True" else False

        # User Menu Content
        sync_app_documentation_url = ir_config.sudo().get_param('sync_app_documentation_url')
        sync_app_documentation_dev_url = ir_config.sudo().get_param('sync_app_documentation_dev_url')
        sync_app_support_url = ir_config.sudo().get_param('sync_app_support_url')
        sync_app_account_title = ir_config.sudo().get_param('sync_app_account_title')
        sync_app_account_url = ir_config.sudo().get_param('sync_app_account_url')
        group_show_author_in_apps = True if ir_config.sudo().get_param('group_show_author_in_apps') == "True" else False
        # Left Menu Footer
        sync_app_show_poweredby = True if ir_config.sudo().get_param('sync_app_show_poweredby') == "True" else False
        # Easy to swich lang
        sync_app_show_lang = True if ir_config.sudo().get_param('sync_app_show_lang') == "True" else False

        res.update(
            # Rebranding
            sync_app_company_fevicon=sync_app_company_fevicon,
            sync_app_system_name=sync_app_system_name,
            sync_app_system_url=sync_app_system_url,
            sync_app_system_title=sync_app_system_title,

            # User Menu
            sync_app_show_debug=sync_app_show_debug,
            sync_app_show_documentation=sync_app_show_documentation,
            sync_app_show_documentation_dev=sync_app_show_documentation_dev,
            sync_app_show_support=sync_app_show_support,
            sync_app_show_account=sync_app_show_account,
            sync_app_show_poweredby=sync_app_show_poweredby,
            group_show_author_in_apps=group_show_author_in_apps,

            # User Menu Content
            sync_app_documentation_url=sync_app_documentation_url,
            sync_app_documentation_dev_url=sync_app_documentation_dev_url,
            sync_app_support_url=sync_app_support_url,
            sync_app_account_title=sync_app_account_title,
            sync_app_account_url=sync_app_account_url,

            # Easy to swich lang
            sync_app_show_lang=sync_app_show_lang
        )
        return res

    def set_values(self):
        self.ensure_one()
        ir_config = self.env['ir.config_parameter']
        company_url = 'http://www.yourcompany.com'
        # Rebranding
        ir_config.set_param("sync_app_company_fevicon", self.sync_app_company_fevicon or "")
        ir_config.set_param("sync_app_system_name", self.sync_app_system_name or "yourcompany")
        ir_config.set_param("sync_app_system_title", self.sync_app_system_title or "yourcompany")
        ir_config.set_param("sync_app_system_url", self.sync_app_system_url or company_url)

        # User Menu
        ir_config.set_param("sync_app_show_debug", self.sync_app_show_debug or "False")
        ir_config.set_param("sync_app_show_documentation", self.sync_app_show_documentation or "False")
        ir_config.set_param("sync_app_show_documentation_dev", self.sync_app_show_documentation_dev or "False")
        ir_config.set_param("sync_app_show_support", self.sync_app_show_support or "False")
        ir_config.set_param("sync_app_show_account", self.sync_app_show_account or "False")
        ir_config.set_param("sync_app_show_poweredby", self.sync_app_show_poweredby or "False")
        ir_config.set_param("group_show_author_in_apps", self.group_show_author_in_apps or "False")
        # User Menu Content
        ir_config.set_param("sync_app_documentation_url",
                            self.sync_app_documentation_url or company_url)
        ir_config.set_param("sync_app_documentation_dev_url",
                            self.sync_app_documentation_dev_url or company_url)
        ir_config.set_param("sync_app_support_url", self.sync_app_support_url or company_url)
        ir_config.set_param("sync_app_account_title", self.sync_app_account_title or company_url)
        ir_config.set_param("sync_app_account_url", self.sync_app_account_url or company_url)

        # Easy to swich lang
        ir_config.set_param("sync_app_show_lang", self.sync_app_show_lang or "False")
        super(AppThemeConfigSettings, self).set_values()
