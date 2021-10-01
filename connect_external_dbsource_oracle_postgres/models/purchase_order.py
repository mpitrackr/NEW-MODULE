# -*- coding: utf-8 -*-

from odoo import tools, models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    closed_code = fields.Char('Closed Code')
    closed_date = fields.Char('Closed Date')
    po_header_id = fields.Integer('Po Header Id')


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    po_header_id = fields.Integer('Po Header Id')
    po_line_id = fields.Integer('Po line Id')
    oracle_po_line = fields.Integer(string='Oracle PO Line')
    oracle_po_ship_line = fields.Integer(string='Oracle PO Shipment Line')
