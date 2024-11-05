from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = "account.payment"

    # Created to record retention percentages
    comment_withholding = fields.Char('Comment withholding')

    def _get_fiscal_period(self, date):
        str_date = str(date).split('-')
        vals = 'AÑO ' + str_date[0] + ' MES ' + str_date[1]
        return vals

    @api.onchange('journal_id')
    def _onchange_compute_amount_currency(self):
        for rec in self:
            if rec.other_currency and rec.payment_group_id:
                if rec.payment_group_id.payments_amount <= 0:
                    rec.amount = rec.payment_group_id.selected_debt  # Cambiado a selected_debt
                elif rec.payment_group_id and rec.payment_group_id.payments_amount > 0:
                    payments_amount = rec.payment_group_id.selected_debt - rec.payment_group_id.payments_amount
                    rec.amount = rec.company_id.currency_id._convert(
                        payments_amount, rec.currency_id, rec.company_id, rec.date)
            elif not rec.other_currency and rec.payment_group_id:
                rec.amount = rec.payment_group_id.selected_debt  # Cambiado a selected_debt
                if rec.payment_group_id and rec.payment_group_id.payments_amount > 0:
                    payments_amount = rec.payment_group_id.payments_amount - rec.amount
                    rec.amount = rec.payment_group_id.selected_debt - payments_amount

    @api.onchange('date')
    def _onchange_compute_amount_currency_date(self):
        for rec in self:
            if rec.other_currency and rec.payment_group_id:
                rec.amount_company_currency = rec.currency_id._convert(
                    rec.amount, rec.company_id.currency_id,
                    rec.company_id, rec.date)

    def get_amount_untaxed_bs(self):
        for rec in self:
            if rec.reconciled_bill_ids:
                return rec.reconciled_bill_ids.amount_untaxed_bs
            else:
                return 1.00

    def get_amount_total_bs(self):
        for rec in self:
            if rec.reconciled_bill_ids:
                return rec.reconciled_bill_ids.amount_total_bs
            else:
                return 1.00

    def get_amount_tax_bs(self):
        for rec in self:
            if rec.reconciled_bill_ids:
                return rec.reconciled_bill_ids.amount_tax_bs
            else:
                return 1.00

    def action_report_withholding_certificate(self):
        return self.env.ref('l10n_ve_withholding.action_report_withholding_certificate').report_action(self)

    def action_report_withholding_certificate_iva(self):
        return self.env.ref('l10n_ve_withholding.action_report_withholding_certificate_iva').report_action(self)
