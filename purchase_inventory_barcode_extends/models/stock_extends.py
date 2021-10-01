# -*- encoding: utf-8 -*-
from odoo import api, fields, models,_
from datetime import datetime

class StockPicking(models.Model):
    _inherit = "stock.move"

    packing_size = fields.Char('Packing Size')
    transaction_date = fields.Datetime('Transaction Date',default=fields.Date.context_today)
        

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    
    @api.model
    def create(self, vals):
        print("Vals : ",vals)
        return super(StockMoveLine, self).create(vals)

    @api.depends('lot_production_date')
    def _set_lot_production_date(self):
        for record in self:
            if record.lot_id and record.lot_production_date:
                record.lot_id.write({'production_date':record.lot_production_date})
         
    @api.depends('lot_id','lot_id.production_date')
    def _get_lot_production_date(self):
        for record in self:
            record.lot_production_date = ''
            if record.lot_id and record.lot_id.production_date:
                record.lot_production_date = record.lot_id and record.lot_id.production_date or False    
         

    @api.depends('lot_expiry_date')
    def _set_lot_expiry_date(self):
        for record in self:
            if record.lot_id and record.lot_expiry_date:
                record.lot_id.write({'use_date':record.lot_expiry_date})
         
  
    @api.depends('lot_id','lot_id.use_date')
    def _get_lot_expiry_date(self):
        for record in self:
            record.lot_expiry_date = ''
            if record.lot_id and record.lot_id.use_date:
                record.lot_expiry_date = record.lot_id and record.lot_id.use_date or False
         

    @api.depends('packing_size')
    def _set_packing_size(self):
        for record in self:
            if record.move_id and record.packing_size:
                record.move_id.write({'packing_size':record.packing_size})
          
    @api.depends('move_id','move_id.packing_size')
    def _get_packing_size(self):
        for record in self:
            record.packing_size = record.move_id and record.move_id.packing_size or ''    

    
    @api.depends('transaction_date')
    def _set_transaction_date(self):
        for record in self:
            if record.move_id and record.transaction_date:
                record.move_id.write({'transaction_date':record.transaction_date})
                
                
    @api.depends('move_id','move_id.transaction_date')
    def _get_transaction_date(self):
        for record in self:
            record.transaction_date = record.move_id and record.move_id.transaction_date or datetime.now() 
                

    lot_production_date = fields.Date('Lot Production Date',compute='_get_lot_production_date',inverse='_set_lot_production_date',store=True)
    lot_expiry_date = fields.Date('Lot Expiry Date',compute='_get_lot_expiry_date',inverse='_set_lot_expiry_date',store=True)
    packing_size = fields.Char('Packing Size',compute='_get_packing_size',inverse='_set_packing_size',store=True)
    comments = fields.Text('Comments')
    transaction_date = fields.Date('Transaction Date', compute='_get_transaction_date',inverse='_set_transaction_date',store=True)
    
    #add by varun
    product_serial_number = fields.Char('Serial Number')
    
    @api.onchange('product_serial_number')
    def _onchange_product_serial(self):
        #conside serial format : product_code|packing_size|Lot_name|Lot_production_date|Lot_expiry_date
        #Example of QR serial format: NA01A|25kg/bag|NA01A-Lot2|01-OCT-2021|01-OCT-2021
        for record in self:
            if record.product_serial_number:
                serial_number_list = record.product_serial_number.split('|')
                
                #Find Product
                product = self.env['product.product'].search([('default_code','=',serial_number_list[0])])
                record.product_id = product and product.id or False
                
                #Get packing size
                record.packing_size = serial_number_list and serial_number_list[1] or ''
                #Get Lot name
                record.lot_name = serial_number_list and serial_number_list[2] or ''
                #Get Production Date
                production_date = datetime.strptime(serial_number_list and serial_number_list[3], '%d-%b-%Y')
                record.lot_production_date = production_date or ''
                #Get Expiry Date
                expiry_date = datetime.strptime(serial_number_list and serial_number_list[4], '%d-%b-%Y')
                record.lot_expiry_date = expiry_date
                
                
                
    

    def write(self,vals):
        move_datas = {}
        for record in self:
            if record.id not in move_datas:
                move_datas[record.id] = {}
                
            lot_name = vals.get('lot_name') or record.lot_name    
            lot_id = self.env['stock.production.lot'].search([('name','=',lot_name)],limit=1)
            lot_expiry_date = vals.get('lot_expiry_date',False) or record.lot_expiry_date
            lot_production_date = vals.get('lot_production_date',False) or record.lot_production_date
            
            if not record.lot_id and lot_name:
                if lot_id:
                    vals['lot_id'] = lot_id and lot_id.id or False
            move_datas[record.id]['lot_name'] = lot_name
            move_datas[record.id]['lot_id'] = lot_id
            move_datas[record.id]['lot_production_date'] = lot_production_date
            move_datas[record.id]['lot_expiry_date'] = lot_expiry_date
        res = super(StockMoveLine,self).write(vals)
      
        for record in self:
            lot_name = move_datas[record.id].get('lot_name',False)
            lot_id = move_datas[record.id].get('lot_id',False)
            lot_production_date = move_datas[record.id].get('lot_production_date',False)
            lot_expiry_date = move_datas[record.id].get('lot_expiry_date',False)
            if lot_name:
                if lot_id:
                    lot_id.write({'production_date': lot_production_date or '','use_date':lot_expiry_date})
            else:
                if record.lot_id:
                    record.lot_id.write({'production_date': lot_production_date or '','use_date':lot_expiry_date})
        return res

  
    def _action_done(self):
        data_dict = {}
        for record in self:
            lot_expiry_date = record.lot_expiry_date
            lot_production_date = record.lot_production_date
            data_dict.update({record.id:{'lot_expiry_date':lot_expiry_date,'lot_production_date':lot_production_date}})
        
        res = super(StockMoveLine,self)._action_done()
        for record in self:
            if record.lot_id:
                record.lot_id.write({'use_date':data_dict.get(record.id).get('lot_expiry_date'),'production_date':data_dict.get(record.id).get('lot_production_date')})
        return res
        

class StockPickingExtends(models.Model):
    _inherit = "stock.picking"
     
    partner_ref = fields.Char('Orcale PO Number',related='purchase_id.partner_ref')

    
    
   
