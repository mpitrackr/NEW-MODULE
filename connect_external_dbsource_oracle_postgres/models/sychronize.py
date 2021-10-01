# -*- coding: utf-8 -*-

from odoo import tools, models, fields, api, _
from odoo.exceptions import ValidationError
import psycopg2
from datetime import datetime, date, timedelta
import logging

_logger = logging.getLogger(__name__)

try:
    import cx_Oracle
except:
    _logger.debug(
        'Oracle libraries not available. Please install "cx_Oracle"\
                 python package by "pip3 install cx_Oracle".'
    )


class SychronizeSychronize(models.Model):
    _name = "sychronize.sychronize"
    _description = "Sychronization"

    name = fields.Char(string="Name", required=True)
    url = fields.Char(string="Address IP", required=True)
    port = fields.Char(string="Port", required=True)
    username = fields.Char(string="Utilisateur", required=True)
    password = fields.Char(string="Mot de passe", required=True)
    database = fields.Char(string="Database")
    schedule = fields.Boolean(string="Schedule")
    query = fields.Text(string="Query String", help="E.g: Select * FROM helpdesk; ")
    sync_sale_tracker = fields.Integer('Sync SO Tracker')
    sync_purchase_tracker = fields.Integer('Sync PO Tracker')
    sync_ris_tracker = fields.Integer('Sync RIS Tracker')
    options = fields.Selection(
        [
            ("sale", "Sale"),
            ("purchase", "Purchase"),
            ("ris", "RIS"),
        ],
        string="Sync Option",
        required=True,
        default="purchase",
    )
    connection = fields.Selection(
        [("oracle", "Oracle"), ("pg", "PostgreSQL")],
        string="Connect To",
        default="oracle",
        required=True,
    )
    state = fields.Selection(
        [("draft", "Draft"), ("verified", "Verified")], string="Status", default="draft"
    )
    order_by = fields.Text(string="Order By", help="E.g: order by ooha.order_number, oola.line_number; ")


    def verify_connection(self):
        for record in self:
            # Postgresql Connection Test
            if record.connection == "pg":
                connection = False
                try:
                    connection = psycopg2.connect(
                        user=record.username,
                        password=record.password,
                        host=record.url,
                        port=record.port,
                        database=record.database,
                    )
                    cursor = connection.cursor()
                except (Exception, psycopg2.Error) as error:
                    raise ValidationError(
                        _("Error while connecting to PostgreSQL:\n %s")
                        % tools.ustr(error)
                    )
                finally:
                    # closing database connection.
                    if connection:
                        self.schedule = True
                        cursor.close()
                        connection.close()
                        record.state = "verified"
                        return {
                            "name": "Message",
                            "type": "ir.actions.act_window",
                            "view_type": "form",
                            "view_mode": "form",
                            "res_model": "pop.message",
                            "target": "new",
                            "context": {"default_name": "Connection Successful!"},
                        }
            # Oracle Connection Test
            if record.connection == "oracle":
                connection = False
                try:
                    dsn_tns = cx_Oracle.makedsn(self.url, self.port, service_name=self.database)
                    connection = cx_Oracle.connect(user=self.username, password=self.password, dsn=dsn_tns)
                    cursor = connection.cursor()
                except (Exception, psycopg2.Error) as error:
                    raise ValidationError(
                        _("Error while connecting to Oracle:\n %s") % tools.ustr(error)
                    )
                finally:
                    # closing database connection.
                    if connection:
                        self.schedule = True
                        cursor.close()
                        connection.close()
                        record.state = "verified"
                        return {
                            "name": "Message",
                            "type": "ir.actions.act_window",
                            "view_type": "form",
                            "view_mode": "form",
                            "res_model": "pop.message",
                            "target": "new",
                            "context": {"default_name": "Connection Successful!"},
                        }
        return True

    def makeDictFactory(self, cursor):
        columnNames = [d[0] for d in cursor.description]
        def createRow(*args):
            return dict(zip(columnNames, args))
        return createRow

    def _get_query_data(self, type):
        dict_result = []
        dsn_tns = cx_Oracle.makedsn(self.url, self.port, service_name=self.database)
        connection = cx_Oracle.connect(user=self.username, password=self.password, dsn=dsn_tns)
        cursor = connection.cursor()        

        max_rec_id = 0
        if type == "sale":
            header_id = 'ooha.header_id'
            max_rec_id = self.sync_sale_tracker
        elif type == "po":
            header_id = 'pha.po_header_id'
            max_rec_id = self.sync_purchase_tracker
        else:
            header_id = 's1.batch_no'
            max_rec_id = self.sync_ris_tracker

        # print('\t', max_rec_id, max_rec_id+50000)
        order_by = self.order_by if self.order_by else ''
        try:
            query = self.query + " and "+ header_id + " > " + str(max_rec_id) + " and " + header_id + " < " + str(max_rec_id + 50000) + order_by
            cursor.execute(str(query))
        except:
            query = self.query + "\nWHERE " + header_id + " > " + str(max_rec_id) + " and " + header_id + " < " + str(max_rec_id + 50000) + order_by
            cursor.execute(str(query))
        cursor.rowfactory = self.makeDictFactory(cursor)
        data_all = cursor.fetchall()
        if len(data_all) == 0:
            try:
                get_oracle_data_limit = self.query + " and " + header_id + " > " + str(max_rec_id + 50000) + "order by " + header_id
                cursor.execute(str(get_oracle_data_limit))
            except:
                get_oracle_data_limit = self.query + "\nWHERE " + header_id + " > " + str(max_rec_id + 50000) + "order by " + header_id
                cursor.execute(str(get_oracle_data_limit))
            
            cursor.rowfactory = self.makeDictFactory(cursor)
            get_rec = cursor.fetchone()
            if type == "sale":
                max_rec_id = get_rec.get('SO Header ID') if get_rec else False
            elif type == "po":
                max_rec_id = get_rec.get('PO_HEADER_ID') if get_rec else False
            else:
                max_rec_id = get_rec.get('PICK_SLIP_NO') if get_rec else False

            # print('\t', max_rec_id, max_rec_id+50000)
            if max_rec_id:
                try:
                    query = self.query + " and " + header_id + " >= "+ str(max_rec_id) + " and " + header_id + " < " + str(max_rec_id + 50000) + order_by
                    cursor.execute(str(query))
                except:
                    query = self.query + "\nWHERE " + header_id + " >= " + str(max_rec_id) + " and " + header_id + " < " + str(max_rec_id + 50000) + order_by
                    cursor.execute(str(query))

                cursor.rowfactory = self.makeDictFactory(cursor)
                data_all = cursor.fetchall()
        for row in data_all:
            dict_result.append(dict(row))
        cursor.close()
        connection.close()
        return dict_result

    def sync_vendor_rec(self):
        dsn_tns = cx_Oracle.makedsn(self.url, self.port, service_name=self.database)
        connection = cx_Oracle.connect(user=self.username, password=self.password, dsn=dsn_tns)
        cursor = connection.cursor()
        cursor.execute(str("SELECT vendor_id, vendor_name FROM ap_suppliers"))
        cursor.rowfactory = self.makeDictFactory(cursor)
        data_all = cursor.fetchall()
        Vendor = self.env['res.partner']
        for row in data_all:
            vendor_id = Vendor.search(
                [("name", "=", row["VENDOR_NAME"]), ("vendor_id", "=", row["VENDOR_ID"]), ("supplier_rank", ">", 0)],
                limit=1,
            )
            if not vendor_id:
                vendor_id = Vendor.create({"name": row["VENDOR_NAME"], "vendor_id": row["VENDOR_ID"], "supplier_rank": 1, "company_type": 'company'})
        print('All Suppliers import Successfully.')
        cursor.close()
        connection.close()

    def sync_product_rec(self):
        dsn_tns = cx_Oracle.makedsn(self.url, self.port, service_name=self.database)
        connection = cx_Oracle.connect(user=self.username, password=self.password, dsn=dsn_tns)
        cursor = connection.cursor()
        cursor.execute("SELECT  organization_id, inventory_item_id, primary_uom_code, primary_unit_of_measure, segment1, description FROM \
            mtl_system_items_b msb")
        cursor.rowfactory = self.makeDictFactory(cursor)
        data_all = cursor.fetchall()
        Product = self.env['product.product']
        Uom = self.env["uom.uom"]
        SyncLog = self.env["sychronize.log"]
        for row in data_all:
            if row.get("PRIMARY_UNIT_OF_MEASURE"):
                uom_id = Uom.search([("name", "=", row["PRIMARY_UNIT_OF_MEASURE"])], limit=1)
                if not uom_id:
                    sync_log = "Uom '%s' not found, please add UOM first before sync products!!" % row["PRIMARY_UNIT_OF_MEASURE"]
                    synced_log = SyncLog.search([('sync_log', '=', sync_log)])
                    if not synced_log:
                        SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
                    self.env.cr.commit()
                if uom_id:
                    product_id = Product.search(
                        [("oracle_inventory_item_id", "=", row["INVENTORY_ITEM_ID"])],
                        limit=1,
                    )
                    if not product_id:
                        try:
                            product_id = Product.create({"oracle_organization_id": row["ORGANIZATION_ID"], "oracle_inventory_item_id": row["INVENTORY_ITEM_ID"], "name": row["DESCRIPTION"], "default_code": row["SEGMENT1"], "type": 'product'})
                            product_id.update({"uom_id":uom_id.id})
                        except:
                            sync_log = "Product '%s' with UOM '%s' not synced.\nbecause The default Unit of Measure and the purchase Unit of Measure must be in the same category." % (row["DESCRIPTION"], row["PRIMARY_UNIT_OF_MEASURE"])
                            synced_log = SyncLog.search([('sync_log', '=', sync_log)])
                            if not synced_log:
                                SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
                            self.env.cr.commit()
        print('All Products import Successfully.')
        self.env.cr.commit()
        cursor.close()
        connection.close()

    def sync_purchase_order(self):
        SyncLog = self.env["sychronize.log"]
        try:
            while self._get_query_data("po"):
                purchase_data = self._get_query_data("po")
                Purchase = self.env["purchase.order"]
                Partner = self.env["res.partner"]
                Product = self.env["product.product"]
                Uom = self.env["uom.uom"]
                for purchase in purchase_data:
                    po_open = True
                    if purchase.get("CLOSED_CODE") and purchase["CLOSED_CODE"] == "CLOSED" and purchase.get("ATTRIBUTE15") and purchase["ATTRIBUTE15"] == "Y":
                        po_open = False

                    if purchase and po_open == True:
                        # Vendor create/write
                        if purchase.get("VENDOR_ID"):
                            Domain = [('vendor_id', '=', purchase["VENDOR_ID"], ("supplier_rank", ">", 0))]
                            vendor = Partner.search(Domain, limit=1)
                            if not vendor:
                                self.sync_vendor_rec()
                                vendor = Partner.search(Domain, limit=1)
                            supplier_id = vendor.id
                        elif purchase.get("SUPPLIER"):
                            Domain = [("name", "=", purchase["SUPPLIER"]), ("supplier_rank", ">", 0)]
                            vendor = Partner.search(Domain, limit=1)
                            if not vendor:
                                self.sync_vendor_rec()
                                vendor = Partner.search(Domain, limit=1)
                            supplier_id = vendor.id
                        else:
                            sync_log = 'Issue Accured During synced vendor for PO %s.' % str(purchase["PO_NUMBER"])
                            SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})

                        # product UOM log
                        if purchase.get("UOM"):
                            uom_id = Uom.search([("name", "=", purchase["UOM"])], limit=1)
                            if not uom_id:
                                sync_log = "Uom '%s' not found in the odoo database." % purchase["UOM"]
                                synced_log = SyncLog.search([('sync_log', '=', sync_log)])
                                if not synced_log:
                                    SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
                                    self.env.cr.commit()

                        # product create/write
                        if purchase.get("ITEM_ID"):
                            product_id = Product.search([('oracle_inventory_item_id', '=', purchase["ITEM_ID"])], limit=1)
                            if not product_id:
                                sync_log = 'Product not found with Item-Id "%s" and Description "%s".\nit seems like first you need to import all products from oracle to odoo before sync PO.' % (str(purchase["ITEM_ID"]), str(purchase["ITEM_DESC"]))
                                synced_log = SyncLog.search([('sync_log', '=', sync_log)])
                                if not synced_log:
                                    SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
                        
                        if purchase.get("PO_NUMBER") and supplier_id and product_id:
                            val = {
                                "name": purchase["PO_NUMBER"],
                                "partner_id": supplier_id if supplier_id else False,
                                "closed_code": purchase["CLOSED_CODE"] if purchase.get("CLOSED_CODE") else False,
                                "closed_date": purchase["CLOSED_DATE"] if purchase.get("CLOSED_DATE") else False,
                                "po_header_id": int(purchase["PO_HEADER_ID"]) if purchase.get("PO_HEADER_ID") else False,
                            }
                            line_val = {
                                'order_line': [(0, 0, {
                                    'name': purchase.get("ITEM_DESC"),
                                    'product_id': product_id.id if product_id else False,
                                    'product_uom_qty': purchase.get("QUANTITY"),
                                    'product_qty': purchase.get("QUANTITY"),
                                    'product_uom': product_id.uom_po_id.id,
                                    'price_unit':0.0,
                                    'date_planned': datetime.today(),
                                    "po_header_id": int(purchase["PO_HEADER_ID"]) if purchase.get("PO_HEADER_ID") else False,
                                    "po_line_id": int(purchase["PO_LINE_ID"]) if purchase.get("PO_LINE_ID") else False,
                                    "oracle_po_line": int(purchase["PO_LINE"]) if purchase.get("PO_LINE") else False,
                                    "oracle_po_ship_line": int(purchase["PO_SHIPMENT_LINE"]) if purchase.get("PO_SHIPMENT_LINE") else False,
                                })]
                            }
                            # Purhase Create/Write
                            purchase_id = Purchase.search([("name", "=", purchase["PO_NUMBER"])], limit=1)
                            if not purchase_id:
                                purchase_id = Purchase.create(val)
                                purchase_id.write(line_val)
                            else:
                                purchase_line = purchase_id.order_line.filtered(lambda l: l.po_header_id == purchase["PO_HEADER_ID"] and l.po_line_id == purchase["PO_LINE_ID"] and l.oracle_po_ship_line == int(purchase.get("PO_SHIPMENT_LINE")))
                                if not purchase_line:
                                    purchase_id.write(line_val) 
                    self.sync_purchase_tracker = int(purchase["PO_HEADER_ID"])
                self.env.cr.commit()
        except:
            if not self.query:
                logged = SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': "You haven't wrote the query for sync PO."})
            else:
                sync_log = "Connection time out !\n it seems like VPN not connected or network issue accured."
                is_logged = SyncLog.search([('sync_log', '=', sync_log), ('sync_time', '>=', datetime.today())])
                if not is_logged:
                    SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
            self.env.cr.commit()
            raise ValidationError(_("Something Went Wrong !!\ncheck sychronization log for more detail!"))
        
        # Compare all purchase line synced or not
        self.purchase_line_oracle_compare()
        self.sync_purchase_tracker = 0

        if self._context.get("manual"):
            return {
                "name": "Message",
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "form",
                "res_model": "pop.message",
                "target": "new",
                "context": {
                    "default_name": "Purchase Order sychronisation process is completed!"
                },
            }
        else:
            return True

    def temp_button_to_attribute15_none(self):
        dsn_tns = cx_Oracle.makedsn(self.url, self.port, service_name=self.database)
        connection = cx_Oracle.connect(user=self.username, password=self.password, dsn=dsn_tns)
        cursor = connection.cursor()
        cursor.execute("UPDATE po_headers_all SET attribute15 = 'N' WHERE attribute15 = 'Y'")
        connection.commit()
        cursor.close()
        connection.close()

    def purchase_line_oracle_compare(self):
        dsn_tns = cx_Oracle.makedsn(self.url, self.port, service_name=self.database)
        connection = cx_Oracle.connect(user=self.username, password=self.password, dsn=dsn_tns)
        cursor = connection.cursor()
        odoo_po_ids = self.env['purchase.order'].search([('state', '=', 'draft'), ('po_header_id', '>', 0)])
        SyncLog = self.env["sychronize.log"]
        confirm_po_commit = 0
        for po in odoo_po_ids:
            confirm_po_commit += 1
            query = "SELECT pla.po_line_id, pll.shipment_num, pll.quantity FROM po_headers_all pha JOIN po_lines_all pla ON pla.po_header_id = \
            pha.po_header_id JOIN po_line_locations_all pll ON pll.po_line_id = pla.po_line_id WHERE NVL(pll.closed_code,'OPEN') = 'OPEN' AND \
            pha.authorization_status = 'APPROVED' AND pha.po_header_id = "+ str(po.po_header_id)
            cursor.execute(str(query))
            cursor.rowfactory = self.makeDictFactory(cursor)
            data_all = cursor.fetchall()

            # synced po line update in oracle table
            if po.order_line.mapped('po_line_id'):
                cursor.execute("UPDATE po_lines_all pla SET pla.attribute15='Y' WHERE po_line_id in "+ \
                    str(po.order_line.mapped('po_line_id')).replace('[','(').replace(']',')'))
            
            # when all lines synced in po then update in oracle table
            if data_all and len(data_all) == len(po.order_line):
                cursor.execute("UPDATE po_headers_all pha  SET pha.attribute15='Y' WHERE po_header_id="+ str(po.po_header_id))
                po.button_confirm()
            else:
                sync_log = 'PO %s had not been confirmed because not all po line synced properly.' %(po.name)
                SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
            if (confirm_po_commit%100) == 0:
                self.env.cr.commit()
        self.env.cr.commit()
        connection.commit()
        cursor.close()
        connection.close()

    def reset_connection(self):
        return self.write({"state": "draft"})

    @api.model
    def cron_import_purchase_recs(self):
        for sync in self.env["sychronize.sychronize"].search(
            [
                ("state", "=", "verified"),
                ("connection", "=", "oracle"),
                ("options", "=", "purchase"),
                ("schedule", "=", True),
                ("query", "!=", ''),
            ]
        ):
            sync.sync_purchase_order()

    # --------------- Post receipt values  --------------
    def post_purchase_receipt_data(self):
        SyncLog = self.env['sychronize.log']
        vpn_connected = False
        try:
            dsn_tns = cx_Oracle.makedsn(self.url, self.port, service_name=self.database)
            connection = cx_Oracle.connect(user=self.username, password=self.password, dsn=dsn_tns)
            cursor = connection.cursor()
            vpn_connected = True
            receipts = self.env['stock.picking'].search([('state', '=', 'done'), ('is_sync', '!=', True), ('picking_type_code', '=', 'incoming'), ('partner_id', '!=', False)]) #('origin', '!=', False)
            log = False
            if receipts:
                for receipt in receipts:
                    SYSDATE = datetime(datetime.today().year, datetime.today().month, datetime.today().day, 0, 0)
                    vendor_id = receipt.partner_id.vendor_id
                    if not vendor_id:
                        sync_log = "during post reciept no. '%s', to oracle vendor_id not found for the partner %s" % (receipt.name, receipt.partner_id.name)
                        SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
                    if vendor_id:
                        # get header_interface_id
                        cursor.execute("Select rcv_headers_interface_s.nextval from dual")
                        header_interface_id = cursor.fetchone()[0]
                        
                        # get group_id
                        cursor.execute("Select rcv_interface_groups_s.nextval from dual")
                        group_id = cursor.fetchone()[0]

                        # --Insert Query 1--
                        try:
                            rows = [ (header_interface_id, group_id,'PENDING','VENDOR', 'NEW', SYSDATE, 0, 0, vendor_id, SYSDATE, 'Y', 82) ]
                            cursor.executemany("INSERT INTO rcv_headers_interface (header_interface_id, group_id, processing_status_code, receipt_source_code,transaction_type, LAST_UPDATE_DATE, LAST_UPDATED_BY, LAST_UPDATE_LOGIN, vendor_id, expected_receipt_date, validation_flag, org_id) values(:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12)", rows) 
                        except:
                            sync_log = "Receipt '%s' not post to oracle." % (receipt.name)
                            log = SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
                        
                        for line in receipt.move_line_nosuggest_ids:
                            lots = line.mapped('lot_id')
                            product_item_id = line.product_id.oracle_inventory_item_id
                            if not product_item_id:
                                sync_log = "during post reciept no. '%s' to oracle, oracle_inventory_item_id not found for the product %s" % (receipt.name, receipt.product_id.name)
                                log = SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})

                            # get line_location_id
                            cursor.execute("select line_location_id from po_line_locations_all where po_line_id ="+str(line.move_id.purchase_line_id.po_line_id) + " AND shipment_num = "+str(line.move_id.purchase_line_id.oracle_po_ship_line))
                            line_location_id = cursor.fetchone()[0]

                            # get po_distribution_id
                            cursor.execute("select po_distribution_id from po_distributions_all where line_location_id = "+ str(line_location_id))
                            po_distribution_id = cursor.fetchone()[0]
                            transaction_date = SYSDATE
                            if line.move_id.transaction_date:
                                transaction_date = datetime(line.move_id.transaction_date.year, line.move_id.transaction_date.month, line.move_id.transaction_date.day, 0, 0)

                            # --Insert Query 2--
                            try:
                                # get interface_transaction_id
                                cursor.execute("Select rcv_transactions_interface_s.nextval from dual")
                                interface_transaction_id_2 = cursor.fetchone()[0]

                                line_row = [ (interface_transaction_id_2, SYSDATE, 0, SYSDATE, 0, 0, line.move_id.purchase_line_id.po_header_id, line.move_id.purchase_line_id.po_line_id, product_item_id, line_location_id, po_distribution_id, line.product_uom_id.name, line.qty_done, 'PENDING', 'BATCH', 'PENDING', transaction_date, 'VENDOR', 'IPW', 'PO', 'Y', 'RECEIVE', 'RECEIVE', header_interface_id, group_id, 82, None, line.comments, line.move_id.packing_size) ]
                                cursor.executemany("INSERT INTO rcv_transactions_interface (interface_transaction_id, last_update_date, last_updated_by, creation_date, created_by, last_update_login, po_header_id, po_line_id, item_id, po_line_location_id, po_distribution_id, unit_of_measure, quantity, processing_status_code, processing_mode_code, transaction_status_code, transaction_date, receipt_source_code, to_organization_code, source_document_code, validation_flag, auto_transact_code, transaction_type, header_interface_id, group_id, org_id, parent_interface_txn_id, comments, packing_slip) values(:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27, :28, :29)", line_row)
                                subinventory = line.location_dest_id.location_id.name # WH
                                locator = line.location_dest_id.name # Stock
                            except:
                                sync_log = "[PO: %s]\nduring post reciept no. '%s', at reciept line for product-'%s' is not inserted in the oracle DB." % (receipt.purchase_id.name, receipt.name, line.product_id.name)
                                log = SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
                    
                            # --Insert Query 3--
                            try:
                                if lots:
                                    # get interface_transaction_id
                                    cursor.execute("Select rcv_transactions_interface_s.nextval from dual")
                                    interface_transaction_id_3 = cursor.fetchone()[0]
                                    
                                    line_row_2 = [ (interface_transaction_id_3, SYSDATE, 0, SYSDATE, 0, 0, line.move_id.purchase_line_id.po_header_id, line.move_id.purchase_line_id.po_line_id, product_item_id, line_location_id, po_distribution_id, line.product_uom_id.name, line.qty_done, 'PENDING', 'BATCH', 'PENDING', transaction_date, 'VENDOR', 'IPW', 'PO', 'Y', None, 'INVENTORY', 'ACCEPTED', None, None, 'ACCEPT', None, group_id, 82, interface_transaction_id_2, line.comments, line.move_id.packing_size) ]
                                    cursor.executemany("INSERT INTO rcv_transactions_interface (interface_transaction_id, last_update_date, last_updated_by, creation_date, created_by, last_update_login, po_header_id, po_line_id, item_id, po_line_location_id, po_distribution_id, unit_of_measure, quantity, processing_status_code, processing_mode_code, transaction_status_code, transaction_date, receipt_source_code, to_organization_code, source_document_code, validation_flag, auto_transact_code, destination_type_code, inspection_status_code, subinventory, locator, transaction_type, header_interface_id, group_id, org_id, parent_interface_txn_id, comments, packing_slip) values(:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27, :28, :29, :30, :31, :32, :33)", line_row_2) 
                            except:
                                sync_log = "[PO: %s]\nduring post reciept no. '%s', at reciept line for product-'%s' is not inserted in the oracle DB." % (receipt.purchase_id.name, receipt.name, line.product_id.name)
                                log = SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
                    
                            # --Insert Query 4--
                            try:
                                parent_interface_txn_id = interface_transaction_id_2
                                if lots:
                                    parent_interface_txn_id = interface_transaction_id_3
                                # get interface_transaction_id
                                cursor.execute("Select rcv_transactions_interface_s.nextval from dual")
                                interface_transaction_id_4 = cursor.fetchone()[0]
                                
                                line_row_3 = [ (interface_transaction_id_4, SYSDATE, 0, SYSDATE, 0, 0, line.move_id.purchase_line_id.po_header_id, line.move_id.purchase_line_id.po_line_id, product_item_id, line_location_id, po_distribution_id, line.product_uom_id.name, line.qty_done, 'PENDING', 'BATCH', 'PENDING', transaction_date, 'VENDOR', 'IPW', 'PO', 'Y', None, 'INVENTORY', None, subinventory, locator, 'DELIVER', None, group_id, 82, parent_interface_txn_id, line.comments, line.move_id.packing_size) ]
                                cursor.executemany("INSERT INTO rcv_transactions_interface (interface_transaction_id, last_update_date, last_updated_by, creation_date, created_by, last_update_login, po_header_id, po_line_id, item_id, po_line_location_id, po_distribution_id, unit_of_measure, quantity, processing_status_code, processing_mode_code, transaction_status_code, transaction_date, receipt_source_code, to_organization_code, source_document_code, validation_flag, auto_transact_code, destination_type_code, inspection_status_code, subinventory, locator, transaction_type, header_interface_id, group_id, org_id, parent_interface_txn_id, comments, packing_slip) values(:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27, :28, :29, :30, :31, :32, :33)", line_row_3) 
                            except:
                                sync_log = "[PO: %s]\nduring post reciept no. '%s', at reciept line for product-'%s' is not inserted in the oracle DB." % (receipt.purchase_id.name, receipt.name, line.product_id.name)
                                log = SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
                    
                            # --Insert Query 5--
                            # for move_line in line.move_line_nosuggest_ids:
                            try:
                                if lots and line.lot_id:
                                    cursor.execute("Select mtl_material_transactions_s.nextval from dual")
                                    transaction_interface_id = cursor.fetchone()[0]
                                    lot_number = line.lot_id.name
                                    
                                    # LOT_EXPIRATION_DATE
                                    expiration_date = line.lot_id.use_date
                                    LOT_EXPIRATION_DATE = SYSDATE
                                    if expiration_date:
                                        LOT_EXPIRATION_DATE = datetime(expiration_date.year, expiration_date.month, expiration_date.day, 0, 0)

                                    # ORIGINATION_DATE
                                    org_date = line.lot_id.production_date
                                    ORIGINATION_DATE = SYSDATE
                                    if org_date:
                                        ORIGINATION_DATE = datetime(org_date.year, org_date.month, org_date.day, 0, 0)
                                    
                                    line_row_4 = [ (transaction_interface_id, SYSDATE, 0, SYSDATE, 0, 0, lot_number, line.qty_done, line.move_id.product_uom_qty, LOT_EXPIRATION_DATE, None, ORIGINATION_DATE, 'RCV', interface_transaction_id_4) ]
                                    cursor.executemany("INSERT INTO mtl_transaction_lots_interface (transaction_interface_id, last_update_date, last_updated_by, creation_date, created_by, last_update_login, lot_number, transaction_quantity, primary_quantity, lot_expiration_date, serial_transaction_temp_id, origination_date, product_code, product_transaction_id) values(:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14)", line_row_4) 
                            except:
                                sync_log = "[PO: %s]\nduring post reciept no. '%s', at line of lot no. '%s' is not inserted in the oracle DB.\nNeed to look at such points: \n\t1. Product '%s' Internal reference[%s] should be max 5 character\n\t2. Expiration/Orgination Date\n\t3. Lot No. add properly" % (receipt.purchase_id.name, receipt.name, line.lot_id.name, line.product_id.name, line.product_id.default_code)
                                log = SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
                        if not log:
                            receipt.is_sync = True
                            self.env.cr.commit()
                            connection.commit()
                        log = False
            cursor.close()
            connection.close()
        except:
            if not vpn_connected:
                sync_log = "Connection time out !\n it seems like VPN not connected or network issue accured."
                is_logged = SyncLog.search([('sync_log', '=', sync_log), ('sync_time', '>=', datetime.today())])
                if not is_logged:
                    SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': 'VPN not connected.'})
            self.env.cr.commit()
            raise ValidationError(_("Something Went Wrong !!\ncheck sychronization log for more detail..."))
        if self._context.get("manual"):
            return {
                "name": "Message",
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "form",
                "res_model": "pop.message",
                "target": "new",
                "context": {
                    "default_name": "Purchase Order Receipt posted Successful!"
                },
            }
        else:
            return True

    @api.model
    def cron_post_purchase_reciept(self):
        for sync in self.env["sychronize.sychronize"].search(
            [
                ("state", "=", "verified"),
                ("connection", "=", "oracle"),
                ("options", "=", "purchase"),
                ("schedule", "=", True),
            ]
        ):
            sync.post_purchase_receipt_data()


    # ------------------------- Sync Sale Order -------------------------
    def sync_customer_rec(self):
        dsn_tns = cx_Oracle.makedsn(self.url, self.port, service_name=self.database)
        connection = cx_Oracle.connect(user=self.username, password=self.password, dsn=dsn_tns)
        cursor = connection.cursor()
        cursor.execute(str("SELECT PARTY_NAME, PARTY_ID FROM hz_parties"))
        cursor.rowfactory = self.makeDictFactory(cursor)
        data_all = cursor.fetchall()
        Customer = self.env['res.partner']
        for row in data_all:
            customer_id = Customer.search(
                [("name", "=", str(row["PARTY_NAME"])), ("customer_id", "=", str(row["PARTY_ID"])), ("customer_rank", ">", 0)],
                limit=1,
            )
            if not customer_id:
                customer_id = Customer.create({"name": str(row["PARTY_NAME"]), "customer_id": str(row["PARTY_ID"]), "customer_rank": 1, "company_type": 'company'})
        print('All Customer import Successfully.')
        cursor.close()
        connection.close()

    def sync_sale_order(self):
        SyncLog = self.env["sychronize.log"]
        try:
            while self._get_query_data('sale'):
                sale_data = self._get_query_data('sale')
                Partner = self.env["res.partner"]
                Uom = self.env["uom.uom"]
                Product = self.env["product.product"]
                Sale = self.env["sale.order"]
                for sale in sale_data:
                    # Customer
                    if sale.get("Customer"):
                        customer = Partner.search([("name", "=", sale["Customer"]), ('customer_id', '=', str(sale["Customer ID"])), ("customer_rank", ">", 0)], limit=1)
                        if not customer:
                            # self.sync_customer_rec()
                            customer = Partner.create({"name": sale["Customer"], "customer_id": str(sale["Customer ID"]), "customer_rank": 1, "company_type": 'company'})
                        customer_id = customer.id
                    else:
                        sync_log = 'Issue Accured During synced customer for SO %s.' % str(sale["Sales Order Number"])
                        SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})

                    # product UOM log
                    if sale.get("UOM"):
                        uom_id = Uom.search([("name", "=", sale["UOM"])], limit=1)
                        if not uom_id:
                            sync_log = "Uom '%s' not found in the odoo database." % sale["UOM"]
                            synced_log = SyncLog.search([('sync_log', '=', sync_log)])
                            if not synced_log:
                                SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
                                self.env.cr.commit()    

                    # product create/write
                    if sale.get("Item"):
                        product_id = Product.search([('default_code', '=', sale["Item"])], limit=1)
                        if not product_id:
                            sync_log = 'Product not found with Default code "%s" in odoo database.\nit seems like first you need to import all products from oracle to odoo before sync SO.' % (str(sale["Item"]))
                            synced_log = SyncLog.search([('sync_log', '=', sync_log)])
                            if not synced_log:
                                SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
                            
                    if sale.get("Sales Order Number") and product_id and customer_id:
                        val = {
                            "name": sale["Sales Order Number"],
                            "partner_id": customer_id if customer_id else False,
                            "so_header_id": int(sale["SO Header ID"]) if sale.get("SO Header ID") else False,
                        }
                        line_val = {
                            'order_line': [(0, 0, {
                                'name': sale.get("Description"),
                                'product_id': product_id.id if product_id else False,
                                'product_uom_qty': sale.get("Quantity"),
                                'qty_delivered': sale.get("Quantity"),
                                'product_uom': product_id.uom_po_id.id,
                                'price_unit':0.0,
                                "so_header_id": int(sale["SO Header ID"]) if sale.get("SO Header ID") else False,
                                "oracle_so_line": int(sale["Sales Order Line"]) if sale.get("Sales Order Line") else False,
                                "oracle_shipment_number": int(sale["Shipment Line Number"]) if sale.get("Shipment Line Number") else False,
                                'tax_id': [(6, 0, [])],
                            })]
                        }

                        # Sale Create/Write
                        sale_id = Sale.search([("name", "=", sale["Sales Order Number"])], limit=1)
                        if not sale_id:
                            sale_id = Sale.create(val)
                            sale_id.write(line_val)
                        else:
                            sale_line = sale_id.order_line.filtered(lambda l: l.so_header_id == sale["SO Header ID"] and l.oracle_so_line == sale["Sales Order Line"] and\
                                         l.oracle_shipment_number == int(sale.get("Shipment Line Number")))
                            if not sale_line:
                                sale_id.write(line_val)
                        # sale_id.action_confirm()
                self.env.cr.commit()
                self.sync_sale_tracker = int(sale["SO Header ID"])
            self.env.cr.commit()
        except:
            if not self.query:
                logged = SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': "You haven't wrote the query for sync PO."})
            else:
                sync_log = "Connection time out !\n it seems like VPN not connected or network issue accured."
                is_logged = SyncLog.search([('sync_log', '=', sync_log), ('sync_time', '>=',datetime.today())])
                if not is_logged:
                    SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
                pass
            self.env.cr.commit()
            raise ValidationError(_("Something Went Wrong !!\ncheck sychronization log for more detail!"))
        
        # Compare all so line synced or not
        self.sale_orderline_inbound()
        self.sync_sale_tracker = 0

        if self._context.get("manual"):
            return {
                "name": "Message",
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "form",
                "res_model": "pop.message",
                "target": "new",
                "context": {
                    "default_name": "Sale Order sychronisation process is completed!"
                },
            }
        else:
            return True

    def sale_orderline_inbound(self):
        dsn_tns = cx_Oracle.makedsn(self.url, self.port, service_name=self.database)
        connection = cx_Oracle.connect(user=self.username, password=self.password, dsn=dsn_tns)
        cursor = connection.cursor()
        odoo_so_ids = self.env['sale.order'].search([('state', '=', 'draft'), ('so_header_id', '>', 0)])
        SyncLog = self.env["sychronize.log"]
        count = 0
        for so in odoo_so_ids:
            count += 1
            for line in so.order_line:
                try:
                    sales_order_number = str(so.name)
                    shipment_line_number = str(line.oracle_so_line) + '.' + str(line.oracle_shipment_number)
                    query = "select xx_Sale_Order_St(%s, %s) from  dual" % (sales_order_number, shipment_line_number)
                    cursor.execute(str(query))


                except:
                    sync_log = "oracle_so_line or oracle_shipment_number not stored in SO Number '%s' " % (so.name)
                    SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
            
            so.action_confirm()
            pick = self.env['stock.picking'].search([('sale_id', '=', so.id)])    
            for move in pick.move_ids_without_package:
                move_line_val = {
                        'move_line_ids_without_package': [(0, 0, {
                            'picking_id': pick.id,
                            'product_id': move.product_id.id if move.product_id else False,
                            'product_uom_id': move.product_id.uom_po_id.id,
                            'product_uom_qty': 0,
                            'qty_done': 0.0,
                            'picking_code': 'outgoing', 
                            'state': 'assigned',
                            'reference': pick.name,
                            'origin': so.name,
                            'oracle_so_line': move.oracle_so_line, 
                            'move_id': move.id,
                            'location_id':  move.location_id.id,
                            'location_dest_id': move.location_dest_id.id,
                        })]
                    }
                pick.write(move_line_val)


            if (count%100) == 0:
                self.env.cr.commit()
        self.env.cr.commit()
        connection.commit()
        cursor.close()
        connection.close()

    # Sync SO Cron
    @api.model
    def cron_import_sale_recs(self):
        for sync in self.env["sychronize.sychronize"].search(
            [
                ("state", "=", "verified"),
                ("connection", "=", "oracle"),
                ("options", "=", "sale"),
                ("schedule", "=", True),
                ("query", "!=", ''),
            ]
        ):
            sync.sync_sale_order()
            
    # ------------------------- Post sale receipt values  -------------------------
    def post_sale_receipt_data(self):
        SyncLog = self.env['sychronize.log']
        vpn_connected = False
        try:
            dsn_tns = cx_Oracle.makedsn(self.url, self.port, service_name=self.database)
            connection = cx_Oracle.connect(user=self.username, password=self.password, dsn=dsn_tns)
            cursor = connection.cursor()
            vpn_connected = True
            receipts = self.env['stock.picking'].search([('state', '=', 'done'), ('is_sync', '!=', True), ('picking_type_code', '=', 'outgoing'), \
            ('partner_id', '!=', False)]) #('origin', '!=', False)
            log = False
            if receipts:
                for receipt in receipts:

                    for line in receipt.move_line_ids_without_package:
                        SYSDATE = datetime(datetime.today().year, datetime.today().month, datetime.today().day, 0, 0)

                        transaction_date = SYSDATE
                        if line.transaction_date:
                            transaction_date = datetime(line.transaction_date.year, line.transaction_date.month, line.transaction_date.day, 0, 0)

                        from_location_vals = line.location_id.complete_name.split('/')    #['IPW', 'BW_FG', 'B-FO']

                        to_location_vals = line.location_dest_id.complete_name.split('/') # ['Partner Locations', 'Customers']

                        expiration_date = line.lot_id.use_date
                        LOT_EXPIRATION_DATE = SYSDATE
                        if expiration_date:
                            LOT_EXPIRATION_DATE = datetime(expiration_date.year, expiration_date.month, expiration_date.day, 0, 0)

                        from_org_code = from_location_vals[0] or None
                        from_subinventory = from_location_vals[1] or None
                        from_locator = from_location_vals[2] or None
                        from_inv_item = line.product_id.oracle_inventory_item_id  or None
                        qty = line.qty_done  or None
                        uom = line.product_uom_id.name  or None
                        to_org_code = to_location_vals[0] or None
                        to_subinventory = to_location_vals[1] or None
                        to_locator = to_location_vals[2] if to_location_vals and len(to_location_vals) >= 3 else None
                        lot_number = line.lot_id.name if line.lot_id else None
                        lot_expiration_date = expiration_date  or None
                        transaction_date = transaction_date  or None
                        reference = receipt.reference or None # Reference (custom field, please add at header location) 
                        source = None
                        reason = receipt.reason or None

                        rows = [ (from_org_code, from_subinventory, from_locator, from_inv_item, qty, uom, to_org_code, \
                            to_subinventory, to_locator, lot_number, lot_expiration_date, transaction_date, reference, source, reason) ]
                        
                        query  = '''INSERT INTO XX_INV_DIRECT_ORG_TRAN 
                                    (
                                    from_org_code, 
                                    from_subinventory, 
                                    from_locator, 
                                    from_inv_item,
                                    qty, 
                                    uom, 
                                    to_org_code,
                                    to_subinventory,
                                    to_locator,
                                    lot_number, 
                                    lot_expiration_date,
                                    transaction_date, 
                                    reference, 
                                    source, 
                                    reason
                                    ) values(:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15)'''
                        cursor.executemany(query, rows) 
                        if not log:
                            receipt.is_sync = True
                            self.env.cr.commit()
                            connection.commit()
                        log = False
            cursor.close()
            connection.close()
        except:
            if not vpn_connected:
                sync_log = "Connection time out!\n it seems like VPN not connected or network issue accured."
                is_logged = SyncLog.search([('sync_log', '=', sync_log), ('sync_time', '>=', datetime.today())])
                if not is_logged:
                    SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': 'VPN not connected.'})
            self.env.cr.commit()
            raise ValidationError(_("Something Went Wrong !!\ncheck sychronization log for more detail..."))
        if self._context.get("manual"):
            return {
                "name": "Message",
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "form",
                "res_model": "pop.message",
                "target": "new",
                "context": {
                    "default_name": "Sale Order Receipt posted Successful!"
                },
            }
        else:
            return True

    # Post SO Cron
    @api.model
    def cron_post_sale_reciept(self):
        for sync in self.env["sychronize.sychronize"].search(
            [
                ("state", "=", "verified"),
                ("connection", "=", "oracle"),
                ("options", "=", "sale"),
                ("schedule", "=", True),
                ("query", "!=", ''),
            ]
        ):
            sync.post_sale_receipt_data()

    def static_query_execute(self):
        dsn_tns = cx_Oracle.makedsn(self.url, self.port, service_name=self.database)
        connection = cx_Oracle.connect(user=self.username, password=self.password, dsn=dsn_tns)
        cursor = connection.cursor()
        # try:
        # cursor.execute(self.query)
        

        # cursor.execute(str("select * from XX_SALE_ORDERS_LIST"))
        try:
            cursor.execute(str(self.query))
            cursor.rowfactory = self.makeDictFactory(cursor)
            res = cursor.fetchall()
            for rec in res:
                print('\t\t        ', rec)
            self.env['sychronize.log'].create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': res})
        except:
            cursor.execute(str(self.query))
        self.env.cr.commit()
        connection.commit()
        print('\n\t   DONE    ')
        cursor.close()
        connection.close()

    # ------------------------- Sync Internal Transfer -------------------------
    def sync_ris_order(self):
        SyncLog = self.env["sychronize.log"]
        try:
            while self._get_query_data('ris'):
                data = self._get_query_data('ris')

                Uom = self.env["uom.uom"]
                Pick = self.env["stock.picking"]
                Product = self.env["product.product"]
                Location = self.env["stock.location"]
                PickingType = self.env["stock.picking.type"]
                
                for rec in data:
                    print('============', rec)
                    # product UOM log
                    if rec.get("UOM"):
                        uom_id = Uom.search([("name", "=", rec["UOM"])], limit=1)
                        if not uom_id:
                            sync_log = "Uom '%s' not found in the odoo database." % rec["UOM"]
                            synced_log = SyncLog.search([('sync_log', '=', sync_log)])
                            if not synced_log:
                                SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
                                self.env.cr.commit()    

                    # product create/write
                    product_id = False
                    if rec.get("ITEM_CODE"):
                        product_id = Product.search([('default_code', '=', rec["ITEM_CODE"])], limit=1)
                        if not product_id:
                            sync_log = 'Product not found with Default code "%s" in odoo database.\nit seems like first you need to import all\
                             products from oracle to odoo before sync SO.' % (str(rec["ITEM_CODE"]))
                            synced_log = SyncLog.search([('sync_log', '=', sync_log)])
                            if not synced_log:
                                SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
                    
                    location_dest_id = False
                    if rec.get('REQUESTING_PRODUCTION'):
                        location_dest_id = Location.search([('name', '=', rec['REQUESTING_PRODUCTION'])])
                    if not rec.get('REQUESTING_PRODUCTION') or not location_dest_id:
                        sync_log = 'Dest. Location " %s " not exist in Database' % rec.get('REQUESTING_PRODUCTION')
                        synced_log = SyncLog.search([('sync_log', '=', sync_log)])
                        if not synced_log:
                            SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})

                    location_id = Location.search([('name', '=', "IPW")])
                    if not location_id:
                        SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': "Location 'IPW' not exist in Database."})

                    picking_type_id = PickingType.search([('code', '=', 'internal'), ('default_location_src_id', '=', location_id.id)], limit=1)

                    if product_id and location_dest_id and location_id and picking_type_id:
                        val = {

                            "origin": rec["PICK_SLIP_NO"],
                            "batch_number": rec["BATCH_NO"],
                            "requesting_production": rec["REQUESTING_PRODUCTION"],
                            'location_id':  location_id.id,
                            'location_dest_id': location_dest_id.id,
                            'picking_type_id': picking_type_id.id
                        }
                        line_val = {
                            'move_ids_without_package': [(0, 0, {
                                'name': product_id.name,
                                'product_id': product_id.id if product_id else False,
                                'product_uom': product_id.uom_po_id.id,
                                'required_qty': rec.get("REQUIRED_QUANTITY"),
                                'onhand_qty': rec.get("ONHAND_QUANTITY"),
                                'requested_qty': rec.get("RESERVATION_QUANTITY"),
                                'location_id':  location_id.id,
                                'location_dest_id': location_dest_id.id,
                            })]
                        }

                        # Sale Create/Write
                        pick_id = Pick.search([("origin", "=", rec["PICK_SLIP_NO"])], limit=1)
                        if not pick_id:
                            pick_id = Pick.create(val)
                            pick_id.write(line_val)
                        else:
                            picking_line = pick_id.move_ids_without_package.filtered(lambda l: l.picking_id.origin == rec["PICK_SLIP_NO"])
                            if not picking_line:
                                pick_id.write(line_val)

                        self.env.cr.commit()
                self.env.cr.commit()
                self.sync_ris_tracker = int(rec["PICK_SLIP_NO"])
            self.env.cr.commit()
        except:
            if not self.query:
                SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': "You haven't wrote the query for sync PO."})
            else:
                sync_log = "Connection time out !\n it seems like VPN not connected or network issue accured."
                is_logged = SyncLog.search([('sync_log', '=', sync_log), ('sync_time', '>=', datetime.today())])
                if not is_logged:
                    SyncLog.create({'name': self.name, 'sync_id': self.id, 'sync_time': datetime.now(), 'sync_log': sync_log})
            self.env.cr.commit()
            raise ValidationError(_("Something Went Wrong !!\ncheck sychronization log for more detail!"))
        
        # Compare all so line synced or not
        # self.sale_orderline_inbound()
        self.sync_ris_tracker = 0

        if self._context.get("manual"):
            return {
                "name": "Message",
                "type": "ir.actions.act_window",
                "view_type": "form",
                "view_mode": "form",
                "res_model": "pop.message",
                "target": "new",
                "context": {
                    "default_name": "RIS sychronisation process is completed!"
                },
            }
        else:
            return True

    @api.model
    def cron_import_ris_recs(self):
        for sync in self.env["sychronize.sychronize"].search(
            [
                ("state", "=", "verified"),
                ("connection", "=", "oracle"),
                ("options", "=", "ris"),
                ("schedule", "=", True),
                ("query", "!=", ''),
            ]
        ):
            sync.sync_ris_order()
