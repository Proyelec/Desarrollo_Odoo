from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from collections import defaultdict

class AccountMoveLineWithHoldings(models.Model):
    _inherit = "account.move.line"

    tsc_cod_retencion_islr = fields.Char(string="ISLR withholding code")
    move_id = fields.Many2one('account.move', string='Journal Entry', ondelete='set null', required=False)

    @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'currency_id')
    def _compute_totals(self):
        for line in self:
            if line.display_type != 'product':
                line.price_total = line.price_subtotal = False

            # Compute 'price_subtotal'.
            line_discount_price_unit = line.price_unit * (1 - (line.discount / 100.0))
            subtotal = line.quantity * line_discount_price_unit

            # Compute 'price_total' only if `move_id` is set
            if line.tax_ids and line.move_id:
                taxes_res = line.tax_ids.compute_all(
                    line_discount_price_unit,
                    quantity=line.quantity,
                    currency=line.currency_id,
                    product=line.product_id,
                    partner=line.partner_id,
                    is_refund=line.is_refund,
                )
                line.price_subtotal = taxes_res['total_excluded']

                tax_iva = 0.0

                for tax in line.tax_ids:
                    amount = line.price_unit * tax.amount / 100
                    if 'iva' in tax.name.lower() and line.move_id.invoice_tax_id:
                        amount_iva = (amount * line.move_id.invoice_tax_id.amount / 100) * line.quantity
                        tax_iva += amount_iva

                line.price_total = taxes_res['total_included'] + tax_iva
            else:
                line.price_total = line.price_subtotal = subtotal

    def reconcile(self):
        # Check that each line has an account if move_id is set
        for line in self:
            if line.move_id and not line.account_id:
                raise ValidationError(_("La línea contable {} no tiene una cuenta configurada.").format(line.name))

        res = super().reconcile()
        # Additional logic can go here if necessary

        return res
