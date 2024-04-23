from odoo import fields, models, api
from datetime import datetime, timedelta

class Cron(models.Model):
    _name='cron.odoo'

    def update_expired_odoo(self):
        expiration = self.env['ir.config_parameter'].search([('key','=','database.expiration_date')])
        if expiration.exists():
            date_time = datetime.now()
            update_today = datetime(date_time.year,date_time.month,date_time.day,date_time.hour,date_time.minute,date_time.second) + timedelta(days= 24)
            
            vals = {
                'value': str(update_today),
            }
            expiration.write(vals)

    