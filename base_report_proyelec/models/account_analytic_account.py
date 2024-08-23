from datetime import datetime, timedelta
from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError
from odoo.tools import SQL


class AccountMove(models.Model):
    _inherit = 'account.analytic.account'
    
        
    #Inv Purch
    def action_view_vendor_bill_reporPDF(self,total = False):
        self.ensure_one()
        query = self.env['account.move.line']._search([('move_id.move_type', 'in', self.env['account.move'].get_purchase_types())])
        query.add_where(
            SQL(
                "%s && %s",
                [str(self.id)],
                self.env['account.move.line']._query_analytic_accounts(),
            )
        )
        query_string, query_param = query.select('DISTINCT account_move_line.move_id')
        self._cr.execute(query_string, query_param)
        move_ids = self.env['account.move'].browse([line.get('move_id') for line in self._cr.dictfetchall()])
        if total:
            total_amount_no_tax = sum(move_ids.mapped('amount_untaxed_signed')) if move_ids else 0
            return abs(total_amount_no_tax)
            
        else:
            return move_ids
    
    #Inv Sale
    def action_view_invoice_reporPDF(self,sale_order=False):
        self.ensure_one()
        totalORderAmount = 0
        query = self.env['account.move.line']._search([('move_id.move_type', 'in', self.env['account.move'].get_sale_types())])
        query.add_where(
            SQL(
                "%s && %s",
                [str(self.id)],
                self.env['account.move.line']._query_analytic_accounts(),
            )
        )
        query_string, query_param = query.select('DISTINCT account_move_line.move_id')
        self._cr.execute(query_string, query_param)

        move_ids = self.env['account.move'].browse([line.get('move_id') for line in self._cr.dictfetchall()])
        
        if sale_order and move_ids:
            
            for move in move_ids:
                if move.invoice_origin:
                    order_id = self.env['sale.order'].search([('name','=',move.invoice_origin)])
                    if order_id:   
                        totalORderAmount += sum(order_id.order_line.mapped('price_subtotal'))
                    return totalORderAmount
        else:
            total_amount_no_tax = sum(move_ids.mapped('amount_untaxed_signed')) if move_ids else 0
            return total_amount_no_tax

        return totalORderAmount
    
    def getEstimateCost(self):
        for rec in self:
            total = 0
            if  rec.crossovered_budget_line:
                for line in rec.crossovered_budget_line:
                    if line.planned_amount < 0:
                        total+= line.planned_amount
                        
            return abs(total)           
                    
    def getEstimateRevenue(self):#Ganancia
        for rec in self:
            total = 0
            if  rec.crossovered_budget_line:
                for line in rec.crossovered_budget_line:
                    if line.planned_amount > 0:
                        total+= line.planned_amount
                        
            return total  - self.getEstimateCost()  
        
    def getRealUtility(self):
        return self.action_view_invoice_reporPDF() - self.action_view_vendor_bill_reporPDF(True)
        
      
        
        