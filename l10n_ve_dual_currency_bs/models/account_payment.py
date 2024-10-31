# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging
import requests
from decimal import Decimal, ROUND_DOWN

_logger = logging.getLogger(__name__)

class accountPayment(models.Model):
    _inherit = 'account.payment'

    currency_ref_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.ref('base.VEF'))

    selected_financial_debt_currency = fields.Monetary(
        string="Monto en deuda en BS.",
        currency_field='currency_ref_id',
        help="Monto de la deuda en bolívares."
    )

    @api.model
    def getRate(self):
        res_currency_id = self.env['res.currency'].sudo().search([('name','=','VEF'),('active','=',True)], limit=1)
        if res_currency_id and res_currency_id.rate_ids:
            rate_day = res_currency_id.rate_ids.sorted('name', reverse=True)[:1]
            tx = Decimal(str(rate_day.company_rate))
            tx_amount = tx.quantize(Decimal('1.00'), rounding=ROUND_DOWN)
            return tx_amount
        else:
            return 1.00

    tax_day = fields.Monetary(
        string='Tasa del día', 
        digits=(16, 3),
        currency_field='currency_ref_id',
        default=getRate,
    )

    amount_total_bs = fields.Monetary(
        string="Importe en BS.", 
        store=True, 
        compute='_compute_amounts_bs', 
        currency_field='currency_ref_id',
        tracking=4
    )
    
    rel_code_currency_id = fields.Char(related='currency_id.name', string='Codigo moneda')

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        """
        Este método se ejecuta cuando cambia el diario.
        Si el diario está en BS, asigna el monto de la deuda en BS directamente a `amount_total_bs`.
        """
        for payment in self:
            if payment.journal_id.currency_id and payment.journal_id.currency_id.name == 'VEF':
                # Asigna directamente el monto de la deuda en BS
                payment.amount_total_bs = payment.selected_financial_debt_currency
            else:
                # Si no es en VEF, deja amount_total_bs igual al valor de amount
                payment.amount_total_bs = payment.amount

    @api.depends('tax_day', 'amount', 'rel_code_currency_id')
    def _compute_amounts_bs(self):
        """
        Método para calcular el importe en BS. Usa directamente `selected_financial_debt_currency`
        si está en BS, o `amount * tax_day` si está en USD.
        """
        for payment in self:
            if payment.rel_code_currency_id == 'USD' and payment.tax_day > 0:
                # Calcula el monto en bolívares cuando la moneda es USD
                payment.amount_total_bs = round(payment.amount * payment.tax_day, 3)
            elif payment.rel_code_currency_id != 'VEF':
                # Cuando es BS, simplemente asigna el monto de la deuda en BS
                payment.amount_total_bs = payment.selected_financial_debt_currency
            else:
                payment.amount_total_bs = 0.0
                
        # # Verificación adicional para evitar la división por cero
        # if payment.amount_company_currency != 0:
        #     payment.other_calculated_field = round(
        #         1 / payment.amount_company_currency, 3
        #     ) * round(payment.tax_day, 3)
        # else:
        #     payment.other_calculated_field = 0.0







