# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_sync = fields.Boolean('Sync ?')
    reference = fields.Char('reference')
    batch_number = fields.Char("Batch Number")
    requesting_production = fields.Char("Requesting Production")


class StockMove(models.Model):
    _inherit = "stock.move"

    # oracle_po_line = fields.Integer(string='Oracle Order Line')
    # oracle_po_ship_line = fields.Integer(string='Oracle PO Shipment Line')
    picking_code = fields.Selection(related='picking_id.picking_type_id.code', readonly=True, store=True)
    transaction_date = fields.Date(string='Transaction Date')
    oracle_so_line = fields.Integer(string='Oracle Order Line', related='sale_line_id.oracle_so_line')
    oracle_po_line = fields.Integer(string='Oracle PO Line', related='purchase_line_id.oracle_po_line')
    oracle_po_ship_line = fields.Integer(string='Oracle PO Shipment Line', related='purchase_line_id.oracle_po_ship_line')
    oracle_so_ship_line = fields.Integer(string='Oracle SO Shipment Line', related='sale_line_id.oracle_shipment_number')
    
    required_qty = fields.Integer('Required Qty')
    onhand_qty = fields.Integer('Onhand Qty')
    requested_qty = fields.Integer('Requested Qty')
    # @api.model
    # def create(self, vals):
    #     if vals.get('purchase_line_id'):
    #         p_line = self.env['purchase.order.line'].browse(vals['purchase_line_id'])
    #         so_line = p_line.oracle_po_line if p_line.oracle_po_line else False
    #         ship_line = p_line.oracle_po_ship_line if p_line.oracle_po_ship_line else False
    #         vals.update({'oracle_po_line': so_line, 'oracle_po_ship_line': ship_line})

    #     if vals.get('sale_line_id'):
    #         s_line = self.env['sale.order.line'].browse(vals['sale_line_id'])
    #         so_line = s_line.oracle_so_line if s_line.oracle_so_line else False
    #         ship_line = s_line.oracle_shipment_number if s_line.oracle_shipment_number else False
    #         vals.update({'oracle_so_line': so_line, 'oracle_po_ship_line': ship_line})
    #     print('\n\n\n\t\t\t\t          -------VALD     -----------          ', vals)
    #     return super(StockMove, self).create(vals)
