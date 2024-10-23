# -*- coding: utf-8 -*-
from odoo import models, fields, osv , api
from odoo.exceptions import UserError, ValidationError
import logging
import requests
from decimal import Decimal, ROUND_DOWN
_logger = logging.getLogger(__name__)

"""
    in this code We validate the available quantities and send it to the API.
    
"""


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    amount_untaxed_bs = fields.Float(string="Dual Base Imponible Bs.", store=True, compute='_compute_amounts_bs', tracking=5, digits=(16, 2))
    amount_tax_bs = fields.Float(string="Dual Impuesto Bs", store=True, compute='_compute_amounts_bs',digits=(16, 2))
    amount_total_bs = fields.Float(string="Dual Total BS", store=True, compute='_compute_amounts_bs', tracking=4,digits=(16, 2))
    currency_ref_id = fields.Many2one('res.currency', string='Dual Moneda', default=lambda self: self.env.ref('base.VEF'),digits=(16, 2))
    amount_residual_bs = fields.Monetary(
        string='Dual Bs. Monto Deudor',
        compute='_compute_amounts_bs', 
        store=True,
        digits=(16, 2)
    )
    
    type_report_currency  = fields.Selection(
            [
                ('usd', 'Dolares.'), 
                ('bs',  'Bolívares'),
                ('usd_bs', 'Dual'),
            ] ,
            default = "usd", 
            string = "Totales en factura (PDF)"
        )

        
    related_currency_name  = fields.Char(
        string='moneda del documento',
        related='currency_id.name', readonly=True, store=True, precompute=True)

    
    display_tax_currency = fields.Boolean(string='Mostrar Tasa del día (PDF)', default = True, )
    

    @api.model
    def getRate(self):
        res_currency_id = self.env['res.currency'].sudo().search([('name','=','VEF'),('active','=',True)], limit=1)
        if res_currency_id and res_currency_id.rate_ids:
            rate_day = res_currency_id.rate_ids.sorted('name', reverse=True)[:1]
            tx = Decimal(str(rate_day.company_rate))
            tx_amount = tx.quantize(Decimal('1.00'), rounding=ROUND_DOWN)
            return tx_amount
        else :
            return   1.00
        
    tax_day  = fields.Float(
        string='Tasa del día',
        default = getRate,
        states = {'sale': [('readonly', True)]},
        digits=(16, 4),
    )


    @api.model
    def create(self, vals):
        logging.info(vals)
        if vals.get('invoice_origin',False):
            order_id = self.env['sale.order'].search([
                ('name','=',vals.get('invoice_origin')),
                ('company_id','=',self.env.user.company_id.id)
                ])
            if order_id :
                vals.update({'tax_day':order_id.tax_day})
            else:
                order_id = self.env['purchase.order'].search([
                    ('name','=',vals.get('invoice_origin')),
                    ('company_id','=',self.env.user.company_id.id)
                ])
                if order_id :
          
                    vals.update({'tax_day':order_id.tax_day})
                    
        return super(AccountMove, self).create(vals)

    ##DEESDE AQUI
    
    def calcular_totales_por_impuesto(self):
        impuestos_totales = {}
        totalBaseImponible = 0.00
        for order in self:
            
            for line in order.invoice_line_ids:
                subtoal_amount_bs = Decimal(str(line.subtoal_amount_bs))
                totalBaseImponible+=line.subtoal_amount_bs
                for impuesto in line.tax_ids:
                    if impuesto.amount !=0:#vamos hacer los calculos a distinto Excento
                        impuestod = Decimal(str(impuesto.amount))
                        impuesto_nombre = impuesto.name
                        impuesto_valor = subtoal_amount_bs * impuestod / 100
                        impuesto_valor = impuesto_valor.quantize(Decimal('1.00'), rounding=ROUND_DOWN)
                        if impuesto_nombre in impuestos_totales:
                            impuestos_totales[impuesto_nombre] += impuesto_valor
                        else:
                            impuestos_totales[impuesto_nombre] = impuesto_valor

        return impuestos_totales
    


    def calcular_totales_por_impuesto_USD(self):
        impuestos_totales = {}
        totalBaseImponible = 0.00
        for order in self:
            for line in order.invoice_line_ids:
                for impuesto in line.tax_ids:
                    if impuesto.amount !=0:#vamos hacer los calculos a distinto Excento
                        # logging.info(line.price_subtotal)
                        # logging.info(impuesto.amount)
                        impuesto_nombre = impuesto.name
                        impuesto_valor = (line.price_subtotal * impuesto.amount) / 100
            
                        if impuesto_nombre in impuestos_totales:
                            impuestos_totales[impuesto_nombre] += impuesto_valor
                        else:
                            impuestos_totales[impuesto_nombre] = impuesto_valor

        return impuestos_totales
    
    """
        Funciona para el libro de ventas y compras
    """

    def calcular_base_imponible_por_impuesto_USD(self):
        impuestos_totales = {}
        for order in self:
            for line in order.invoice_line_ids:
                for impuesto in line.tax_ids:
                    if impuesto.amount !=0:#vamos hacer los calculos a distinto Excento
                        # logging.info(line.price_subtotal)
                        # logging.info(impuesto.amount)
                        impuesto_nombre = impuesto.name
                        impuesto_valor = (line.price_subtotal) 
            
                        if impuesto_nombre in impuestos_totales:
                            impuestos_totales[impuesto_nombre] += impuesto_valor
                        else:
                            impuestos_totales[impuesto_nombre] = impuesto_valor

        return impuestos_totales


    @api.depends(
        'amount_untaxed',
        'amount_tax',
        'amount_total',
        'invoice_line_ids.price_unit_bs',
        'invoice_line_ids.currency_rate',
        'invoice_line_ids.tax_base_amount',
        'invoice_line_ids.tax_line_id',
        'invoice_line_ids.price_total',
        'invoice_line_ids.price_subtotal',
        'invoice_payment_term_id',
        'partner_id',
        'currency_id',
        )
    def _compute_amounts_bs(self):
        for move in self:
            
            # move.amount_untaxed_bs = 0.00
            # move.amount_tax_bs = 0.00
            # move.amount_total_bs =  0.00
            # move.amount_residual_bs =  0.00
            if move.currency_id.name == "USD":
                if move.tax_day > 0:
                    # logging.info(move.amount_untaxed)
                    # logging.info(self.calcular_totales_por_impuesto_USD())
            
                    amount_untaxed = Decimal(str(move.amount_untaxed))
                    tax_day = Decimal(str(move.tax_day))
                    totalImpuesto = sum([round(valor,2) for impuesto, valor in self.calcular_totales_por_impuesto().items()])   

                    total_amount_untaxed = sum([line.price_subtotal for line in move.invoice_line_ids])
                    str_total_amount_untaxed = (Decimal(total_amount_untaxed) * Decimal(tax_day)).quantize(Decimal('1.0000'))


                    total_impuestoUSD = sum([round(valor,6) for impuesto, valor in self.calcular_totales_por_impuesto_USD().items()])  
                    str_total_impuestoUSD= (Decimal(total_impuestoUSD) * Decimal(tax_day)).quantize(Decimal('1.0000'))


                    amount_residual = Decimal(str(move.amount_residual ))

                    amount_untaxed_bs = amount_untaxed * tax_day
                    amount_untaxed_bs = amount_untaxed_bs.quantize(Decimal('1.00'), rounding=ROUND_DOWN)
    

                    TOTAL = (Decimal(total_amount_untaxed) * Decimal(tax_day) + (Decimal(total_impuestoUSD) * Decimal(tax_day))  ).quantize(Decimal('1.0000'),rounding=ROUND_DOWN)
                    
                    
                    amount_residual_bs = amount_residual * tax_day
                    amount_residual_bs = amount_residual_bs.quantize(Decimal('1.00'), rounding=ROUND_DOWN)
                    
                    move.amount_untaxed_bs = str_total_amount_untaxed #amount_untaxed_bs
                    move.amount_tax_bs = str_total_impuestoUSD
                    move.amount_total_bs =  TOTAL
                    
                    if move.amount_residual != 0:
                        move.amount_residual_bs = amount_residual_bs
                    else:move.amount_residual_bs =  0.00
                else :
                    move.amount_untaxed_bs = 0.00
                    move.amount_tax_bs = 0.00
                    move.amount_total_bs =  0.00
                    move.amount_residual_bs =  0.00
        
            else:
                move.amount_untaxed_bs = move.amount_untaxed
                move.amount_tax_bs = move.amount_tax
                move.amount_total_bs =  move.amount_total
                move.amount_residual_bs =  0.00
                
    #BOTONES
    
    def _compute_amounts_line_bs(self):
        for line in self.invoice_line_ids:
            line._compute_price_unit_bs_update(line)
            
            
    def updateRateDate(self):
        self._compute_amounts_bs()
        self._compute_amounts_line_bs()
        

    #FIN AQUI

class InheritMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    currency_ref_id = fields.Many2one(
        'res.currency', 
        string='Moneda de Referencial', 
        default=lambda self: self.env.ref('base.VEF')
    )

    price_unit_bs = fields.Monetary(
        string="Bs. Precio", 
        currency_field='currency_ref_id',
        compute='_compute_price_unit_bs',
        digits='Product Price',
        store=True, 
        readonly=False, 
        required=False,
        precompute=True,
    
    )

    subtoal_amount_bs = fields.Monetary(
        string="Bs. Subtotal",
        currency_field='currency_ref_id' ,
        store=True, 
        compute='_compute_amounts_bs', 
        tracking=4)   



    related_tax_day  = fields.Float(
        string='Tasa del día',
        related='move_id.tax_day', readonly=True, store=True, precompute=True,digits=(16, 3)

    )
    
    
    related_currency_id  = fields.Char(
        string='moneda del documento',
        related='move_id.currency_id.name', readonly=True, store=True, precompute=True)


    
    
    @api.depends('price_subtotal')
    def _compute_amounts_bs(self):
        for line in self:
            if line.move_id.currency_id.name == "USD":
                price_subtotal = Decimal(str(line.price_subtotal))
                tax_day = Decimal(str(line.move_id.tax_day))
                
                if line.price_subtotal and  line.move_id.tax_day:
                    subtoal_amount_bs = price_subtotal * tax_day
                    subtoal_amount_bs = subtoal_amount_bs.quantize(Decimal('1.00'), rounding=ROUND_DOWN)
                    line.subtoal_amount_bs= subtoal_amount_bs
            
                else :
                    line.subtoal_amount_bs = 0.00
            else:
                line.subtoal_amount_bs = line.price_subtotal
                          
                

    def _compute_price_unit_bs_update(self,line):
            price_subtotal = Decimal(str(line.price_unit))
            tax_day = Decimal(str(line.move_id.tax_day))  
            if line.price_unit and  line.move_id.tax_day:
                price_unit_bs = price_subtotal * tax_day
                price_unit_bs = price_unit_bs.quantize(Decimal('1.00'), rounding=ROUND_DOWN)
                line.price_unit_bs = float(price_unit_bs)
            elif line.product_id:
                line.price_unit_bs = line.product_id.price_bs
            else :
                line.price_unit_bs = 0.00
                
                
    @api.depends('product_id', 'price_unit',)
    def _compute_price_unit_bs(self):
        for line in self:
            if line.move_id.currency_id.name == "USD":
                if line.price_unit and  line.move_id.tax_day:
                    price_unit = Decimal(str(line.price_unit))
                    tax_day = Decimal(str(line.move_id.tax_day))
                    price_unit_bs = price_unit * tax_day
                    price_unit_bs = price_unit_bs.quantize(Decimal('1.00'), rounding=ROUND_DOWN)
                    line.price_unit_bs = price_unit_bs
                elif line.product_id:
                    line.price_unit_bs = line.product_id.price_bs
                else :
                    line.price_unit_bs = 0.00
            else:
                line.price_unit_bs = line.price_unit
                      