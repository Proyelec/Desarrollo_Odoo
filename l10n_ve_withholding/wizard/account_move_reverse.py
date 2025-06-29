# -*- coding: utf-8 -*-


from odoo import models, fields, api
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _inherit = 'account.move.reversal'


    def _prepare_default_reversal(self, move):
        reverse_date = self.date or move.date
        vals = {
            'ref': _('Reversal of: %(move_name)s, %(reason)s', move_name=move.name, reason=self.reason)
                if self.reason
                else _('Reversal of: %s', move.name),
            'date': reverse_date,
            'invoice_date_due': reverse_date,
            'invoice_date': move.is_invoice(include_receipts=True) and reverse_date or False,
            'journal_id': self.journal_id.id,
            'invoice_payment_term_id': None,
            'invoice_user_id': move.invoice_user_id.id,
            'auto_post': 'at_date' if reverse_date > fields.Date.context_today(self) else 'no',
            'l10n_ve_document_number': ""
        }
        # Forzar amount_currency a 0 para evitar la validación de Odoo
        vals['line_ids'] = []
        for line in move.line_ids:
            line_vals = line.copy_data()[0]
            line_vals['amount_currency'] = 0.0
            vals['line_ids'].append((0, 0, line_vals))
        return vals


    #TODO: ver si esto es necesario.
    # def reverse_moves(self):
    #     """ Forzamos el seteo limpio"""
    #     res = super(AccountMoveReversal, self).reverse_moves()
    #     #Nunca esta pasando por aqui.
    #     for rec in self:
    #         self.move_ids.l10n_ve_document_number = ""
    #     return res
