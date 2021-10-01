# -*- encoding: utf-8 -*-
from odoo import api, fields, models, tools,_
import base64
import csv
from datetime import datetime
import os
from pytz import timezone
from tempfile import NamedTemporaryFile

class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    is_export_to_server = fields.Boolean('Is Export To Server')

    def generate_csv_file_from_receipt(self):
        picking_type_id = self.env['stock.picking.type'].search([('name','=','Receipts')],limit=1)
        file_process_log = self.env['file.process.log']
        transaction_log_obj = self.env['file.transaction.log']
        picking_obj = self.env['stock.picking']
        server_obj = self.env['sftp.server']
        picking_ids = picking_obj.search([('is_export_to_server','=',False),('picking_type_id','=',picking_type_id.id)])
        picking_dic = []
        list_of_process_order =[]
        list_of_process_order_ids = []
        export_time = datetime.now()
        converted_time = export_time.strftime('%Y%m%d_%H%M%S')
        file_name= converted_time +".csv"
            
        if picking_ids:
            job_id=file_process_log.with_context({'company_id':self.env.user.company_id.id}).create({
                                            'filename':file_name,
                                            'name':'Receipt Export',})    
            try:
                for picking in picking_ids:
                    for move_line in picking.move_line_ids_without_package:
                        location_1=''
                        location_2=''
                        location_3=''
                        if picking.location_dest_id:
                            location_1 = picking.location_dest_id.name
                            location_2 = picking.location_dest_id and picking.location_dest_id.location_id and picking.location_dest_id.location_id.name or ''
                            location_3 = picking.location_dest_id and picking.location_dest_id.location_id and picking.location_dest_id.location_id and picking.location_dest_id.location_id.location_id and picking.location_dest_id.location_id.location_id.name or ''  
                        lot_name=''
                        lot_expiry_date=''
                        lot_production_date=''
                        if move_line.lot_id:
                            lot_name=move_line.lot_id.name
                            lot_expiry_date=move_line.lot_id.use_date or ''
                            lot_production_date=move_line.lot_id.production_date or ''
                        data_list=[picking.purchase_id.partner_ref or '',move_line.move_id.oracle_po_line or '',move_line.move_id.oracle_po_ship_line or '',move_line.product_id.uom_id.name or '',picking.partner_id.name or '',move_line.product_id.default_code or '',move_line.product_id.name or '',move_line.product_uom_qty or 0,location_1,location_2,location_3,picking.date_done or '',lot_name,lot_expiry_date,lot_production_date,picking.note or '',move_line.move_id.packing_size or '']
                        picking_dic.append(data_list)
                        list_of_process_order.append(picking.name)
                        list_of_process_order_ids.append(picking.id)
                
                if list_of_process_order_ids:
                    with open(file_name, 'w+', newline ='') as file:
                        header = ['Oracle PO Number', 'Oracle PO Line', 'Oracle PO Shipment Line','UOM','Vendor','Internal Reference','Product Name','Quantity (Done)','Location (Parent)','Location (1st Child)','Location (2nd Child)','Transaction Date','Lot Number','Lot Expiry Date','Lot Production Date','Comments','Packing Size'] 
                        writer = csv.writer(file,delimiter=';')
                        writer.writerow(header)
                        writer.writerows(picking_dic)
                    data = ''    
                    with open(file_name,'r') as file:
                        data = file.read()
                    if data:
                        server_id = self.env['sftp.server'].search([('id','=',1)],limit=1) 
                        if server_id: 
                            sftp_client = server_id.authorize_SFTP()
                            sftp =None
                            if sftp_client:
                                sftp = sftp_client.open_sftp()
                                if sftp:
                                    data_file = NamedTemporaryFile(delete=False)
                                    data_file.file.write(bytes(data,'utf-8'))
                                    data_file.close()
                                    sftp.put(data_file.name,'%s/%s' %(server_id.path,file_name))
                                    process_order_list = picking_obj.browse(list(set(list_of_process_order_ids)))
                                    if process_order_list:
                                        process_order_list.write({'is_export_to_server':True})
                                    transaction_log_obj.create(
                                                    {   'skip_line':False,
                                                        'job_id':job_id.id,
                                                        'message':'list of process order is '+','.join(list(set(list_of_process_order))),
                                                        'row_number':'',
                                                    })
                            else:
                                transaction_log_obj.create(
                                        {'skip_line':True,
                                            'job_id':job_id.id,
                                            'message':'Server configuration error %s ' %(s),
                                            'row_number':'',
                                            })                                
                        else:
                            transaction_log_obj.create(
                                        {
                                            'skip_line':True,
                                            'job_id':job_id.id,
                                            'message':'Please enter a server information',
                                            'row_number':'',
                                            })
                            job_id.write({'message':"orders did not processed successfully due to some Mismatch details"})                                 
            except Exception as e:
                transaction_log_obj.create(
                                    {
                                        'skip_line':True,
                                        'job_id':job_id.id,
                                        'message':str(e),
                                        'row_number':'',
                                        })
                job_id.write({'message':"orders did not processed successfully due to some Mismatch details"})                        
            
        
                