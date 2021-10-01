# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    production_date = fields.Datetime('Lot Production Date')
