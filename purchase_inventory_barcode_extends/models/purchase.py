# -*- encoding: utf-8 -*-


from odoo import api, fields, models, tools
import base64
import csv
from datetime import datetime

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # def generate_purchase_order(self):
    #     server_obj = self.env['sftp.server']
    #     list_of_file = [] 
    #     sftp =None
    #     purchase_obj = self.env['purchase.order']
    #     vendor_obj =self.env['res.partner']
    #     product_obj = self.env['product.product']
    #     product_uom_obj = self.env['uom.uom']
    #     error_history = {}
    #     server_id = server_obj.search([('id','=',1)],limit=1) 
    #     if server_id:
    #         sftp_client = server_id.authorize_SFTP()
    #         if sftp_client:
    #             sftp = sftp_client.open_sftp()
    #             if sftp and server_id.purchase_path:
    #                 sftp.chdir(server_id.purchase_path)
    #                 for remote_data in sftp.listdir(server_id.purchase_path):
    #                     if remote_data.strip().endswith('.csv'):
    #                         list_of_file.append(remote_data)
    #     for file in list_of_file:    
    #         # file_path = '/home/simbeez/purchase.csv'
    #         file_path = server_id.purchase_path+'/'+file
    #         with open(file_path, 'r') as file:
    #             reader = csv.reader(file)
    #             purchase_order_dict ={}
    #             generate_purchase_order_dict = {}
    #             row_number=1
    #             for row in reader:
    #                 if not row[0] in purchase_order_dict.keys():
    #                     purchase_order_dict.update({row[0]:[]})
    #                 row.insert(len(row),row_number)    
    #                 product_line_dic = purchase_order_dict[row[0]]
    #                 product_line_dic.append(row)
    #                 row_number+=1
    #             generate_order_list=[]
    #             for key,values in purchase_order_dict.items():
    #                 order_data ={}
    #                 vendor_id = vendor_obj.search([('name','=',values[0][4])],limit=1)
    #                 if not vendor_id:
    #                     error_history.update({values[0][len(values[0])-1]:'row number %s vendor not found %s '%(values[0][len(values[0])-1],values[0][4])})
    #                     continue
    #                 order_data.update({'partner_id':vendor_id.id,'date_order':datetime.now()})
    #                 line_list=[]
    #                 for data in values:
    #                     line_dict={}
    #                     product_id = product_obj.search([('default_code','=',data[5])],limit=1)
    #                     if not product_id:
    #                         error_history.update({data[0][len(data[0])-1]:'Row %s of Product not found %s '%(data[0][len(data[0])-1],data[5])})
    #                         continue
    #                     product_uom_id = product_uom_obj.search([('name','=',data[3])],limit=1)
    #                     if not product_uom_id:
    #                         continue
    #                     line_dict.update({'product_id':product_id.id,'oracle_po_line':data[1],'product_qty':data[2],'name':data[6],'oracle_po_ship_line':data[7],'price_unit':product_id.list_price,'product_uom':product_uom_id.id,'date_planned':datetime.now()})
    #                     line_list.append(line_dict)
    #                 if line_list and order_data:
    #                     try:
    #                         purchase_id = purchase_obj.create(order_data)          
    #                         for line in line_list:
    #                             purchase_id.write({'order_line':[(0,0,line)]}) 
    #                     except Exception as e:
    #                         error_history.update({line[len(data[0])-1]:'Row %s error is %s '%(line[len(data[0])-1],e)})

               

                

        