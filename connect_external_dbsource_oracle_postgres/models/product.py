# -*- coding: utf-8 -*-

from odoo import tools, models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    oracle_organization_id = fields.Char('Organization Id')
    oracle_inventory_item_id = fields.Char('Inventory Item Id')
