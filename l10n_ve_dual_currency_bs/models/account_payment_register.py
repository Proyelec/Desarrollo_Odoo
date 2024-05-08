# -*- coding: utf-8 -*-

from odoo import models, fields, osv , api
import logging

class InhAccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    

    currency_ref_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.ref('base.VEF'))

    @api.model
    def getRate(self):
        account_move = self.env['account.move'].browse(self._context.get('active_ids', []))
        if account_move and account_move.tax_day:
            return round(account_move.tax_day , 3) 
        else :
            return   1.00
        
    tax_day  = fields.Float(
        string='Tasa del día',
        default = getRate,
        digits='Product Price',
    )

    def _create_payments(self):
        res = super(InhAccountPaymentRegister,self)._create_payments()
        res.tax_day = self.tax_day
        return res
    

    amount_total_bs = fields.Monetary(
        string="Total BS.", 
        store=True, 
        compute='_compute_amounts_bs', 
        currency_field='currency_ref_id',
        tracking=4)




    @api.depends('tax_day','amount')
    def _compute_amounts_bs(self):
        for payment in self:

            if payment.tax_day > 0:
                payment.amount_total_bs = round(
                    round(payment.amount,3) * round(payment.tax_day,3),3)

            else :
                payment.amount_total_bs = 0.000

    
