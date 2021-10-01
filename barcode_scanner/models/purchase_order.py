# -*- encoding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import UserError


# class PurchaseOrder(models.Model):
#     _inherit = "purchase.order"

#     oracle_po_no = fields.Integer(string="Oracle PO Number")


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    oracle_po_line = fields.Integer(string='Oracle PO Line')
    oracle_po_ship_line = fields.Integer(string='Oracle PO Shipment Line')



