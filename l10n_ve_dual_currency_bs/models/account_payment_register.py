# -*- coding: utf-8 -*-

from odoo import models, fields, osv , api
import logging

class InhAccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    

    currency_ref_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.ref('base.VEF'))

    def getRate(self):
        # Iterar sobre los registros de account.move
        for account_move in self:
            # Asegurarse de que tax_day existe y ejecutar la lógica deseada
            if account_move.tax_day:
                # Aquí puedes añadir la lógica necesaria, por ejemplo:
                rate = account_move.tax_day  # Ejemplo: obtener la tasa
                # Procesar el campo tax_day según tus necesidades
                return rate  # Retorna el valor si es necesario para un solo registro
        # Opcional: Devuelve un valor por defecto si no se encuentra tax_day
        return 1
        
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

    
