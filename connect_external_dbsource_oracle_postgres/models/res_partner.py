# -*- coding: utf-8 -*-

from odoo import tools, models, fields, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    vendor_id = fields.Char('Oracle vendor Id')
    customer_id = fields.Char('Oracle customer Id')
