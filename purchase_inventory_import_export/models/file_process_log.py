from odoo import models,fields,api,_

class FileProcessLog(models.Model):
    _name="file.process.log"
    _description = "File Process Log"
    _inherit = ['mail.thread']

    _order='id desc'
    
    name = fields.Char("Name")
    filename = fields.Char("File Name")
    create_date = fields.Datetime("Create Date")
    transaction_log_ids = fields.One2many("file.transaction.log","job_id",string="Transactions")
    # operation_type = fields.Selection([('import','Import'),('export','Export')]
    #                                   ,string="Operation")    
    message=fields.Text("Message")
    company_id=fields.Many2one('res.company',string="Company")
    
    # @api.model
    # def create(self,vals):
    #     name = self.env['ir.sequence'].next_by_code('file.process.log') or _('/')
    #     company_id=self._context.get('company_id',self.env.user.company_id.id)
    #     if type(vals)==dict:
    #         vals.update({'name':name,'company_id':company_id})
    #     return super(FileProcessLog,self).create(vals)
    
class TransactionLog(models.Model):
    _name = 'file.transaction.log'
    _rec_name='file_name'
    _order='id desc'
    
    message = fields.Text("Message")
    # operation_type = fields.Selection([('import','Import'),('export','Export')]
    #                                   ,string="Operation",related="job_id.operation_type",store=False,readonly=True)
    remark=fields.Text("Remark")
    create_date = fields.Datetime("Created Date")
    file_name = fields.Char(string="File Name",related="job_id.filename",store=False,readonly=True)
    job_id = fields.Many2one("file.process.log",string="File Process Job")
    skip_line = fields.Boolean("Skip Line")
    company_id=fields.Many2one('res.company',string="Company")
    row_number = fields.Integer('Row No')

    @api.model
    def create(self,vals):
        if type(vals)==dict:
            job_id=vals.get('job_id',False)
            job=job_id and self.env['file.process.log'].browse(job_id) or False
            company_id=job and job.company_id.id or self.env.user.company_id.id
            vals.update({'company_id':company_id})
        return super(TransactionLog,self).create(vals)