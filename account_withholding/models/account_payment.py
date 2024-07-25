##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

class AccountPayment(models.Model):
    _inherit = "account.payment"

    tax_withholding_id = fields.Many2one(
        'account.tax',
        string='Withholding Tax',
        readonly=False,
    )
    withholding_number = fields.Char(
        readonly=False,
        help="If you don't set a number we will add a number automatically "
             "from a sequence that should be configured on the Withholding Tax"
    )
    withholding_base_amount = fields.Monetary(
        string='Withholding Base Amount',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    withholding_base_amount_bs = fields.Monetary(
        string='Withholding Base Amount Bs',
        compute='_compute_withholding_base_amount_bs'
    )

    @api.depends('amount', 'currency_id')  # Asegúrate de que estos campos existan en account.payment
    def _compute_withholding_base_amount_bs(self):
        for rec in self:
            if rec.amount and rec.currency_id:
                rec.withholding_base_amount_bs = rec.amount * rec.currency_id.rate  # Ejemplo de lógica de cálculo
            else:
                rec.withholding_base_amount_bs = 0

    def _get_valid_liquidity_accounts(self):
        res = super()._get_valid_liquidity_accounts()
        if self.tax_withholding_id:
            logging.info(res)
            domain_id = [id.id for id in res]
            logging.info(domain_id)
            rep_lines = self.env['account.tax.repartition.line'].search(
                [
                    ('company_id', '=', self.company_id.id),
                    ('tax_id.type_tax_use', 'in', ['supplier', 'customer']),
                ])
            if rep_lines:
                for ac in rep_lines:
                    domain_id.append(ac.account_id.id)
            logging.info(rep_lines.mapped('account_id'))
            logging.info(domain_id)
            account_ids = self.env['account.account'].browse(domain_id)
            return account_ids

        return res

    def action_post(self):
        without_number = self.filtered(
            lambda x: x.tax_withholding_id and not x.withholding_number)

        without_sequence = without_number.filtered(
            lambda x: not x.tax_withholding_id.withholding_sequence_id)
        if without_sequence:
            raise UserError(_(
                'No puede validar pagos con retenciones que no tengan número '
                'de retención. Recomendamos agregar una secuencia a los '
                'impuestos de retención correspondientes. Id de pagos: %s') % (
                without_sequence.ids))

        # a los que tienen secuencia les setamos el numero desde secuencia
        for payment in (without_number - without_sequence):
            payment.withholding_number = \
                payment.tax_withholding_id.withholding_sequence_id.next_by_id()

        res = super(AccountPayment, self).action_post()
        withholdings = self.filtered(lambda x: x.tax_withholding_id)
        for withholding in withholdings:
            liquidity_lines, counterpart_lines, writeoff_lines = withholding._seek_for_lines()
            rep_line = withholding._get_withholding_repartition_line()
            liquidity_lines.tax_repartition_line_id = rep_line
            liquidity_lines.tax_line_id = rep_line.tax_id
        return res

    def action_draft(self):
        ''' posted -> draft '''
        withholdings = self.filtered(lambda x: x.tax_withholding_id)
        for withholding in withholdings:
            liquidity_lines, counterpart_lines, writeoff_lines = withholding._seek_for_lines()
            liquidity_lines.parent_state = 'draft'
            liquidity_lines.write({
                'tax_repartition_line_id': False,
                'tax_line_id': False,
            })
        return super().action_draft()

    def _get_withholding_repartition_line(self):
        self.ensure_one()
        if ((self.partner_type == 'customer' and self.payment_type == 'inbound') or
                (self.partner_type == 'supplier' and self.payment_type == 'outbound')):
            rep_field = 'invoice_repartition_line_ids'
        else:
            rep_field = 'refund_repartition_line_ids'
        rep_line = self.tax_withholding_id[rep_field].filtered(lambda x: x.repartition_type == 'tax')
        if len(rep_line) != 1:
            raise UserError(
                'En los impuestos de retención debe haber una línea de repartición de tipo tax para pagos y otra'
                'para reembolsos')
        logging.info("======================TEST=================")
        logging.info(rep_line)
        logging.info(rep_line.display_name)
        logging.info(rep_line.tax_id)
        if not rep_line.account_id:
            raise UserError(_('The tax %s dont have account configured on the tax repartition line') % (
                rep_line.tax_id.name))
        return rep_line

    def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=None):
        res = super()._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals, force_balance=force_balance)

        if self.payment_method_code == 'withholding':
            if self.payment_type == 'transfer':
                raise UserError(_('You can not use withholdings on transfers!'))
            rep_line = self._get_withholding_repartition_line()
            res[0]['name'] = self.withholding_number or '/'
            res[0]['account_id'] = rep_line.account_id.id
        return res

    @api.model
    def _get_trigger_fields_to_synchronize(self):
        res = super()._get_trigger_fields_to_synchronize()
        return res + ('withholding_number', 'tax_withholding_id')
