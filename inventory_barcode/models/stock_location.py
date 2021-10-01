# -*- coding: utf-8 -*-

from odoo import models, api


class Location(models.Model):
    _inherit = 'stock.location'

    @api.model
    def get_all_locations_by_barcode(self):
        locations = self.env['stock.location'].search_read(
            [('barcode', '!=', None)], ['display_name', 'barcode', 'parent_path'])
        locationsByBarcode = {location.pop('barcode'): location for location in locations}
        return locationsByBarcode
    