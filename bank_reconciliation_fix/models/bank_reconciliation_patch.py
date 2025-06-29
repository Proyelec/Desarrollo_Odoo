from odoo import models, _
import logging

_logger = logging.getLogger(__name__)

class BankReconciliationReportCustomHandler(models.AbstractModel):
    _inherit = 'account.bank.reconciliation.report.handler'

    def _compute_journal_balances(self, report, options, journal, journal_currency):
        _logger.info('Parche handler activo: _compute_journal_balances ejecutado')
        domain = report._get_options_domain(options, 'normal')
        balance_gl = journal._get_journal_bank_account_balance(domain=domain)[0]
        last_statement, balance_end, difference, general_ledger_not_matching = self._compute_balances(options, journal, balance_gl, journal_currency)
        balance_gl = report.format_value(balance_gl, currency=journal_currency, figure_type='monetary')
        balance_end = report.format_value(balance_end, currency=journal_currency, figure_type='monetary')
        difference = report.format_value(difference, currency=journal_currency, figure_type='monetary')
        return last_statement, balance_gl, balance_end, difference, general_ledger_not_matching 