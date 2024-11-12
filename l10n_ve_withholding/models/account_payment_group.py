from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

class AccountPaymentGroup(models.Model):
    _inherit = "account.payment.group"

    # Campos adicionales de retención
    selected_debt_taxed = fields.Monetary(
        string='Selected Debt Taxed',
        compute='_compute_selected_debt_taxed',
    )
    debt_multicurrency = fields.Boolean(
        string='Debt is in foreign currency?',
        default=False,
    )
    iva = fields.Boolean('¿Aplicar Retención IVA?')
    islr = fields.Boolean('¿Aplicar Retención ISLR?')
    regimen_islr_id = fields.Many2one(
        'seniat.tabla.islr', 
        'Aplicativo ISLR'
    )
    partner_regimen_islr_ids = fields.Many2many(
        'seniat.tabla.islr',
        compute='_compute_partner_regimen_islr',
    )

    # Campo principal para calcular la deuda seleccionada
    selected_debt = fields.Monetary(
        string='Selected Debt',
        compute='_compute_selected_debt',
        currency_field='currency_id',
        store=True,
    )

    @api.depends('to_pay_move_line_ids.amount_residual', 'to_pay_move_line_ids.amount_residual_currency', 'to_pay_move_line_ids.currency_id')
    def _compute_selected_debt(self):
        for rec in self:
            selected_debt = 0.0
            for line in rec.to_pay_move_line_ids:
                # Asegura que se use la moneda de la factura y ajuste el monto residual
                if line.currency_id == rec.currency_id:
                    selected_debt += line.amount_residual
                else:
                    selected_debt += line.amount_residual_currency
            
            # Ajuste de signo según el tipo de partner
            rec.selected_debt = selected_debt * (-1.0 if rec.partner_type == 'supplier' else 1.0)
            # Establecer la moneda en `currency_id` para reflejar la de la factura
            rec.currency_id = rec.to_pay_move_line_ids[0].currency_id if rec.to_pay_move_line_ids else rec.currency_id

    @api.depends(
        'to_pay_move_line_ids.amount_residual',
        'to_pay_move_line_ids.move_id',
        'payment_date',
    )
    def _compute_selected_debt_taxed(self):
        """ Calcula el monto total de deuda que está sujeto a retenciones de IVA """
        for rec in self:
            selected_debt_taxed = 0.0
            for line in rec.to_pay_move_line_ids:
                for tax_line in line.move_id.line_ids:
                    if tax_line.name in ['IVA (16.0%) compras', 'IVA (8.0%) compras']:
                        selected_debt_taxed += tax_line.debit
            rec.selected_debt_taxed = selected_debt_taxed

    @api.depends('partner_id.seniat_regimen_islr_ids')
    def _compute_partner_regimen_islr(self):
        """ Calcula los regímenes de ISLR aplicables si el partner es proveedor """
        for rec in self:
            rec.partner_regimen_islr_ids = (
                rec.partner_id.seniat_regimen_islr_ids if rec.partner_type == 'supplier' 
                else rec.env['seniat.tabla.islr']
            )

    @api.depends(
        'selected_debt', 'unreconciled_amount'
    )
    def _compute_to_pay_amount(self):
        """ Calcula el monto total a pagar sumando `selected_debt` y `unreconciled_amount` """
        for rec in self:
            rec.to_pay_amount = rec.selected_debt + rec.unreconciled_amount

    @api.onchange('to_pay_amount')
    def _inverse_to_pay_amount(self):
        """ Ajusta el monto de `unreconciled_amount` según el monto total a pagar (`to_pay_amount`) """
        for rec in self:
            rec.unreconciled_amount = rec.to_pay_amount - rec.selected_debt

    def compute_withholdings(self):
        """ Aplica la lógica de retención para proveedores """
        for rec in self:
            if rec.partner_type != 'supplier':
                continue
            self.env['account.tax'].with_context(type=None).search([
                ('type_tax_use', '=', rec.partner_type),
                ('company_id', '=', rec.company_id.id),
            ]).create_payment_withholdings(rec)

    def confirm(self):
        """ Confirma el grupo de pagos y aplica retenciones automáticas si están habilitadas """
        res = super(AccountPaymentGroup, self).confirm()
        for rec in self:
            if rec.company_id.automatic_withholdings:
                rec.compute_withholdings()
        return res
