# -*- encoding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import UserError



class SaleOrder(models.Model):
    _inherit = 'sale.order'


    oracle_order_status = fields.Char(string="Oracle Order Status")



class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    oracle_so_line = fields.Integer(string='Oracle Order Line')


