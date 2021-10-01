# -*- coding: utf-8 -*-

from odoo import tools, models, fields, api, _
from datetime import date, timedelta


class SychronizeLog(models.Model):
    _name = "sychronize.log"
    _description = "Sychronization Log"

    name = fields.Char('Sync Portal', readonly="True", required=1)
    sync_id = fields.Many2one('sychronize.sychronize', 'Sychronize', readonly="True", required=1)
    sync_time = fields.Datetime('Sync Time', readonly="True", required=1)
    sync_log = fields.Text('Sync Log', readonly="True", required=1)

    @api.model
    def cron_remove_sychronize_log(self):
    	expired_log_date = (date.today()-timedelta(days=30)).isoformat()
    	expired_logs = self.env["sychronize.log"].search([("sync_time", "<=", expired_log_date)])
    	if expired_logs:
	        for log in expired_logs:
	            log.unlink()
