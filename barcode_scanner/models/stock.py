# -*- encoding: utf-8 -*-

from odoo import fields, api, models
from odoo.exceptions import UserError

class Stock(models.Model):
    _inherit = 'stock.picking'

    reason = fields.Char('Reason')

    def on_barcode_scanned(self, barcode):
        if not self.env.company.nomenclature_id:
            # Logic for products
            raise UserError(_('barcode method called %s .' %(barcode)))
            barcode_split = barcode.split('|')
            item_code = ''
            lot_number = ''
            lot_production_date = ''
            expiry_date = ''

            if barcode_split:
                item_code = barcode_split[2]
                lot_number = barcode_split[3]
                lot_production_date = barcode_split[4]
                expiry_date = barcode_split[5]

            product = self.env['product.product'].search(['|', ('barcode', '=', barcode), ('default_code', '=', item_code)], limit=1)
            if product:
                if self._check_product(product):
                    return

            product_packaging = self.env['product.packaging'].search([('barcode', '=', barcode)], limit=1)
            if product_packaging.product_id:
                if self._check_product(product_packaging.product_id,product_packaging.qty):
                    return

            # Logic for packages in source location
            if self.move_line_ids:
                package_source = self.env['stock.quant.package'].search([('name', '=', barcode), ('location_id', 'child_of', self.location_id.id)], limit=1)
                if package_source:
                    if self._check_source_package(package_source):
                        return

            # Logic for packages in destination location
            package = self.env['stock.quant.package'].search([('name', '=', barcode), '|', ('location_id', '=', False), ('location_id','child_of', self.location_dest_id.id)], limit=1)
            if package:
                if self._check_destination_package(package):
                    return

            # Logic only for destination location
            location = self.env['stock.location'].search(['|', ('name', '=', barcode), ('barcode', '=', barcode)], limit=1)
            if location and location.search_count([('id', '=', location.id), ('id', 'child_of', self.location_dest_id.ids)]):
                if self._check_destination_location(location):
                    return
        else:
            parsed_result = self.env.company.nomenclature_id.parse_barcode(barcode)
            if parsed_result['type'] in ['weight', 'product']:
                if parsed_result['type'] == 'weight':
                    product_barcode = parsed_result['base_code']
                    qty = parsed_result['value']
                else: #product
                    product_barcode = parsed_result['code']
                    product_item_code = product_barcode.split('|')
                    if product_item_code:
                        product_item_code = product_item_code[2]
                    qty = 1.0
                product = self.env['product.product'].search(['|', ('barcode', '=', product_barcode), ('default_code', '=', product_item_code)], limit=1)
                if product:
                    if self._check_product(product, qty):
                        return

            if parsed_result['type'] == 'package':
                if self.move_line_ids:
                    package_source = self.env['stock.quant.package'].search([('name', '=', parsed_result['code']), ('location_id', 'child_of', self.location_id.id)], limit=1)
                    if package_source:
                        if self._check_source_package(package_source):
                            return
                package = self.env['stock.quant.package'].search([('name', '=', parsed_result['code']), '|', ('location_id', '=', False), ('location_id','child_of', self.location_dest_id.id)], limit=1)
                if package:
                    if self._check_destination_package(package):
                        return

            if parsed_result['type'] == 'location':
                location = self.env['stock.location'].search(['|', ('name', '=', parsed_result['code']), ('barcode', '=', parsed_result['code'])], limit=1)
                if location and location.search_count([('id', '=', location.id), ('id', 'child_of', self.location_dest_id.ids)]):
                    if self._check_destination_location(location):
                        return

            product_packaging = self.env['product.packaging'].search([('barcode', '=', parsed_result['code'])], limit=1)
            if product_packaging.product_id:
                if self._check_product(product_packaging.product_id,product_packaging.qty):
                    return

        return {'warning': {
            'title': _('Wrong barcode'),
            'message': _('The barcode "%(barcode)s" doesn\'t correspond to a proper product, package or location.') % {'barcode': barcode}
        }}


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    production_date = fields.Date(string='Lot Production Date')




class StockMove(models.Model):
    _inherit = 'stock.move'

    picking_code = fields.Selection(related='picking_id.picking_type_id.code', readonly=True, store=True)
    oracle_so_line = fields.Integer(string='Oracle Order Line')
    oracle_po_line = fields.Integer(string='Oracle PO Line', related='purchase_line_id.oracle_po_line')
    oracle_po_ship_line = fields.Integer(string='Oracle PO Shipment Line', related='purchase_line_id.oracle_po_ship_line')
   


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    oracle_so_line = fields.Integer(string='Oracle Order Line')

