from odoo import models,fields,api,_
from odoo.exceptions import UserError
import base64
import io
from datetime import datetime
try:
    import paramiko
except ImportError:
    raise ImportError('This module needs paramiko to automatically write backups to the FTP through SFTP. '
        'Please install paramiko on your system. (sudo pip3 install paramiko)')


class SFTPServer(models.Model):
    _name="sftp.server"
    
    name=fields.Char("Server name",required=True)
    sftp_host=fields.Char("Host",required=True)
    sftp_username=fields.Char("User Name",required=True)
    sftp_password=fields.Char("Password",required=True)
    sftp_port=fields.Char("Port",required=True)
    is_passive_mode=fields.Boolean("Passive Mode",default=True)
    path_name=fields.Char("Path Name",required=True)
    path=fields.Char("Path",required=True)
    attachment_id = fields.Many2one('ir.attachment','Attachment File')
    server_file = fields.Binary('Private File')
    file_name =fields.Char('File Name')
    purchase_path=fields.Char("Purchase Path",required=True)
    archived_path = fields.Char("Archived Path ",required=True)
    

    @api.model
    def create(self, vals):
        if 'server_file' in vals:
            vals_data = {
                    'name':vals['file_name'] or '',
                    'datas':vals['server_file'],
                    'type':'binary',
                    'mimetype':"application/octet-stream",
                    'res_model':'sftp.server',
                    }
            attachment_id = self.env['ir.attachment'].create(vals_data)
            if attachment_id:
                vals.update({'attachment_id':attachment_id.id})
        return super(SFTPServer, self).create(vals)            
         

    def write(self, vals):
        res = super(SFTPServer, self).write(vals)
        if 'server_file' in vals:
            if self.attachment_id:
               self.attachment_id.write({'datas':vals['server_file'],
                                    'name':self.file_name,
                                    'mimetype':"application/octet-stream",
                                   }) 


    def test_server_connection(self):
        self.ensure_one()
        has_failed = False    
        sftp_client = None    
        try:
            sftp_client = self.authorize_SFTP()
        except Exception as e:
            has_failed = True
            raise UserError(_('The server error is : %s ' %(str(e))))
        finally:
            if sftp_client:
                sftp_client.close()

        if not has_failed:
            title = _("Connection Test Succeeded!")
            message = _("Everything seems properly set up!")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': title,
                    'message': message,
                    'sticky': False,
                }
            }

    def authorize_SFTP(self):
        sftp_client = None
        try:
            sftp_client = paramiko.SSHClient()
            sftp_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            private_key_file = self.attachment_id._full_path(self.attachment_id.store_fname)
            k = paramiko.RSAKey.from_private_key_file(private_key_file,self.sftp_password)
            sftp_client.connect(self.sftp_host, self.sftp_port, username = self.sftp_username, pkey=k)
        except Exception as e:
            raise UserError(_('The server error is : %s ' %(str(e))))
        return sftp_client        
           