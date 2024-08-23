from datetime import datetime, timedelta
from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError
from odoo.tools import SQL
import logging 

class AccountMove(models.Model):
    _inherit = 'account.move'
    
        
    def action_get_totalPaymentsPDF(self):
        self.ensure_one()
        pay1 = self.sudo().invoice_payments_widget and self.sudo().invoice_payments_widget['content'] or []
        totalAmountP = 0
        if pay1:
            for p in pay1:
                totalAmountP+= p['amount']
        return totalAmountP
       