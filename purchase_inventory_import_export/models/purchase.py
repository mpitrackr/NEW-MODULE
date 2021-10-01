# -*- encoding: utf-8 -*-
from odoo import api, fields, models, tools,_
import base64
import csv
from datetime import datetime
import os
from pytz import timezone
from tempfile import NamedTemporaryFile

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    def generate_purchase_order(self):
        purchase_obj = self.env['purchase.order']
        vendor_obj =self.env['res.partner']
        product_obj = self.env['product.product']
        product_uom_obj = self.env['uom.uom']
        file_process_log = self.env['file.process.log']
        transaction_log_obj = self.env['file.transaction.log']
        server_obj = self.env['sftp.server']
        list_of_file = []
        export_file = []
        process_file = []
        sftp =None
        error_history = {}
        count = 0
        server_id = server_obj.search([],limit=1) 
        if server_id:
            try:
                sftp_client = server_id.authorize_SFTP()
                if sftp_client:
                    sftp = sftp_client.open_sftp()
                    if sftp and server_id.purchase_path:
                        sftp.chdir(server_id.purchase_path)
                        for remote_data in sftp.listdir(server_id.purchase_path):
                            if remote_data.strip().endswith('.csv'):
                                data_file = NamedTemporaryFile(delete=False)
                                sftp.getfo(remote_data,data_file,None)
                                data_file.close()
                                export_file.append(data_file.name)
                                list_of_file.append(remote_data)
                    else:
                        file_process_log.with_context({'company_id':self.env.user.company_id.id}).create({
                                                    'filename':'',
                                                    'name':'Server autorization error or path not found error'})            
                else:
                    file_process_log.with_context({'company_id':self.env.user.company_id.id}).create({
                                                    'filename':'',
                                                    'name':'Server Configuration Error'})
            except Exception as e:
                file_process_log.with_context({'company_id':self.env.user.company_id.id}).create({
                                        'filename':'',
                                        'name':'Server error %s' %(str(e))})                                                        
        else:
            file_process_log.with_context({'company_id':self.env.user.company_id.id}).create({
                                                'filename':'',
                                                'name':'Server not found'})
        for file_data in export_file: 
            file_path = file_data
            file_name = list_of_file[count]
            count+=1
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                purchase_order_dict ={}
                generate_purchase_order_dict = {}
                job_id=file_process_log.with_context({'company_id':self.env.user.company_id.id}).create({
                                                'filename':file_name,
                                                'name':'Purchase Order Create',})
                row_number=0
                for row in reader:
                    if not row[0] in purchase_order_dict.keys():
                        purchase_order_dict.update({row[0]:[]})
                    row.insert(len(row),row_number)    
                    product_line_dic = purchase_order_dict[row[0]]
                    product_line_dic.append(row)
                    row_number+=1
                generate_order_list=[]
                self.create_attchment_for_file(file,job_id)
                for key,values in purchase_order_dict.items():
                    order_data ={}
                    vendor_id = vendor_obj.search([('name','=',values[0][4])],limit=1)
                    if not vendor_id:
                        transaction_log_obj.create(
                                        {   'skip_line':True,
                                            'job_id':job_id.id,
                                            'message':'%s vendor not found' %(values[0][4]),
                                            'row_number':values[0][len(values[0])-1],
                                        })
                        job_id.write({'message':"File did not processed successfully due to some Mismatch details"})
                        continue
                    order_data.update({'partner_id':vendor_id.id,'date_order':datetime.now()})
                    line_list=[]
                    for data in values:
                        line_dict={}
                        product_id = product_obj.search([('default_code','=',data[5])],limit=1)
                        if not product_id:
                            transaction_log_obj.create(
                                        {   'skip_line':True,
                                            'job_id':job_id.id,
                                            'message':'%s Product not found' %(data[5]),
                                            'row_number':data[0][len(data[0])-1],
                                            })
                            job_id.write({'message':"File did not processed successfully due to some Mismatch details"})
                            continue
                        product_uom_id = product_uom_obj.search([('name','=',data[3])],limit=1)
                        if not product_uom_id:
                            transaction_log_obj.create(
                                        {   'skip_line':True,
                                            'job_id':job_id.id,
                                            'message':'%s Product Unit of Measure is not found' %(data[6]),
                                            'row_number':data[0][len(data[0])-1],
                                            })
                            job_id.write({'message':"File did not processed successfully due to some Mismatch details"})
                            continue
                        line_dict.update({'product_id':product_id.id,'oracle_po_line':data[1],'product_qty':data[2],'name':data[6],'oracle_po_ship_line':data[7],'price_unit':product_id.list_price,'product_uom':product_uom_id.id,'date_planned':datetime.now()})
                        line_list.append(line_dict)
                    if line_list and order_data:
                        try:
                            purchase_id = purchase_obj.create(order_data)          
                            for line in line_list:
                                purchase_id.write({'order_line':[(0,0,line)]})
                            process_file.append(file_name) 
                        except Exception as e:
                            transaction_log_obj.create(
                                        {
                                            'skip_line':True,
                                            'job_id':job_id.id,
                                            'message':'%s error is' %(str(e)),
                                            'row_number':line[len(data[0])-1],
                                            })
                            job_id.write({'message':"File did not processed successfully due to some Mismatch details"})
        if server_id and process_file:
            self.move_to_file_archived_folder(process_file,server_id)

    def create_attchment_for_file(self,file,job):
        if file:
            file.seek(0)
            file_data = file.read()
            time_zone = self.env.user.tz or 'UTC'
            export_time = datetime.now(timezone(time_zone))   
            converted_time = export_time.strftime('%Y%m%d_%H%M%S') 
            file_name='%s_%s.csv'%('file',converted_time)     
            vals = {
                    'name':file_name,
                    'datas':base64.encodestring(bytes(file_data,'utf-8')),
                    'type':'binary',
                    'res_model':'file.process.log',
                    }
            attachment=self.env['ir.attachment'].create(vals)
            job.message_post(body=_("<b>Sales Report File</b>"),attachment_ids=attachment.ids)

    def move_to_file_archived_folder(self,process_file,server_id):
        file_process_log = self.env['file.process.log']
        process_file = list(set(process_file))
        try:
            sftp_client = server_id.authorize_SFTP()
            if sftp_client:
                sftp = sftp_client.open_sftp()
                if sftp and server_id.purchase_path:
                    for filename in process_file:
                        fromname = "%s%s" %(server_id.purchase_path,filename)
                        toname = "%s%s" %(server_id.archived_path,filename)
                        sftp.chdir(server_id.purchase_path)
                        sftp.posix_rename(fromname, toname)
                else:
                    file_process_log.with_context({'company_id':self.env.user.company_id.id}).create({
                                                'filename':'',
                                                'name':'Server autorization error or path not found error'})            
            else:
                file_process_log.with_context({'company_id':self.env.user.company_id.id}).create({
                                                'filename':'',
                                                'name':'Server Configuration Error'})
        except Exception as e:
            file_process_log.with_context({'company_id':self.env.user.company_id.id}).create({
                                    'filename':'',
                                    'name':'Server error %s' %(str(e))})



