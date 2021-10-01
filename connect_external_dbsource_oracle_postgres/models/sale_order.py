
# -*- coding: utf-8 -*-

from odoo import tools, models, fields, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # oracle_so_line = fields.Char('Closed Code')
    # closed_date = fields.Char('Closed Date')
    so_header_id = fields.Integer('SO Header Id')


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    so_header_id = fields.Integer('SO Header Id')
    oracle_so_line = fields.Integer('Oracle Order line')
    oracle_shipment_number = fields.Integer('Oracle Shipment Number')
    