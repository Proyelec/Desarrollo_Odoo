# © 2016 ADHOC SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from decimal import Decimal, ROUND_DOWN

import logging
_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    payment_group_id = fields.Many2one(
        'account.payment.group',
        'Payment Group',
        readonly=True,
    )
    amount_company_currency = fields.Monetary(
        string='Amount on Company Currency',
        compute='_compute_amount_company_currency',
        inverse='_inverse_amount_company_currency',
        currency_field='company_currency_id',
        readonly=False,  # Remover readonly para que no sea solo lectura
    )
    other_currency = fields.Boolean(
        compute='_compute_other_currency',
    )
    force_amount_company_currency = fields.Monetary(
        string='Forced Amount on Company Currency',
        currency_field='company_currency_id',
        copy=False,
    )
    exchange_rate = fields.Float(
        string='Exchange Rate',
        compute='_compute_exchange_rate',
        # readonly=False,
        # inverse='_inverse_exchange_rate',
        digits=(16, 4),
    )
    l10n_ar_amount_company_currency_signed = fields.Monetary(
        currency_field='company_currency_id', compute='_compute_l10n_ar_amount_company_currency_signed')
    # campo a ser extendido y mostrar un nombre detemrinado en las lineas de
    # pago de un payment group o donde se desee (por ej. con cheque, retención,
    # etc)
    payment_method_description = fields.Char(
        compute='_compute_payment_method_description',
        string='Payment Method Desc.',
    )
    available_journal_ids = fields.Many2many(
        comodel_name='account.journal',
        compute='_compute_available_journal_ids'
    )

    label_journal_id = fields.Char(
        compute='_compute_label'
    )

    label_destination_journal_id = fields.Char(
        compute='_compute_label'
    )

    @api.depends('payment_type', 'payment_group_id')
    def _compute_available_journal_ids(self):
        """
        Este metodo odoo lo agrega en v16
        Igualmente nosotros lo modificamos acá para que funcione con esta logica:
        a) desde transferencias permitir elegir cualquier diario ya que no se selecciona compañía
        b) desde grupos de pagos solo permitir elegir diarios de la misma compañía
        NOTA: como ademas estamos mandando en el contexto del company_id, tal vez podriamos evitar pisar este metodo
        y ande bien en v16 para que las lineas de pago de un payment group usen la compañia correspondiente, pero
        lo que faltaria es hacer posible en las transferencias seleccionar una compañia distinta a la por defecto
        """
        journals = self.env['account.journal'].search([
            ('company_id', 'in', self.env.companies.ids), ('type', 'in', ('bank', 'cash'))
        ])
        for pay in self:
            filtered_domain = [('inbound_payment_method_line_ids', '!=', False)] if \
                pay.payment_type == 'inbound' else [('outbound_payment_method_line_ids', '!=', False)]
            if pay.payment_group_id:
                filtered_domain.append(('company_id', '=', pay.payment_group_id.company_id.id))
            pay.available_journal_ids = journals.filtered_domain(filtered_domain)



    @api.depends('payment_method_id')
    def _compute_payment_method_description(self):
        for rec in self:
            rec.payment_method_description = rec.payment_method_id.display_name

    tax_day = fields.Float(
        string='Tasa del día', 
        compute='_compute_tax_day',
        help="Tasa de cambio del día en bolívares."
    )

    @api.depends('company_id')
    def _compute_tax_day(self):
        """
        Computa la tasa del día basada en la moneda VEF de la compañía.
        Si no hay tasa disponible, establece el valor en 1.00.
        """
        for payment in self:
            res_currency = self.env['res.currency'].search([
                ('name', '=', 'VEF'), ('active', '=', True)
            ], limit=1)
            if res_currency and res_currency.rate_ids:
                latest_rate = res_currency.rate_ids.sorted('name', reverse=True)[:1]
                payment.tax_day = Decimal(str(latest_rate.company_rate)).quantize(Decimal('1.00'), rounding=ROUND_DOWN)
            else:
                payment.tax_day = 1.00

    @api.depends('journal_id', 'tax_day', 'payment_type', 'partner_type')
    def _compute_l10n_ar_amount_company_currency_signed(self):
        """
        Calcula el monto en moneda de la compañía. Si el diario es de ID 38 o 39,
        divide `l10n_ar_amount_company_currency_signed` entre `tax_day`.
        """
        for payment in self:
            if payment.payment_type == 'outbound' and payment.partner_type == 'customer' or \
               payment.payment_type == 'inbound' and payment.partner_type == 'supplier':
                payment.l10n_ar_amount_company_currency_signed = -payment.amount_company_currency
            else:
                payment.l10n_ar_amount_company_currency_signed = payment.amount_company_currency
            

    @api.depends('currency_id')
    def _compute_other_currency(self):
        for rec in self:
            rec.other_currency = False
            if rec.company_currency_id and rec.currency_id and \
               rec.company_currency_id != rec.currency_id:
                rec.other_currency = True

    @api.onchange('payment_group_id')
    def onchange_payment_group_id(self):
        # now we change this according when use save & new the context from the payment was erased and we need to use some data.
        # this change is due this odoo change https://github.com/odoo/odoo/commit/c14b17c4855fd296fd804a45eab02b6d3566bb7a
        if self.payment_group_id:
            self.date = self.payment_group_id.payment_date
            self.partner_type = self.payment_group_id.partner_type
            self.partner_id = self.payment_group_id.partner_id
            self.payment_type = 'inbound' if self.payment_group_id.partner_type  == 'customer' else 'outbound'
            self.amount = self.payment_group_id.payment_difference

    @api.depends('amount', 'other_currency', 'amount_company_currency')
    def _compute_exchange_rate(self):
        for rec in self:
            if rec.other_currency:
                rec.exchange_rate = rec.amount and (
                    rec.amount_company_currency / rec.amount) or 0.0
            else:
                rec.exchange_rate = False

    # this onchange is necesary because odoo, sometimes, re-compute
    # and overwrites amount_company_currency. That happends due to an issue
    # with rounding of amount field (amount field is not change but due to
    # rouding odoo believes amount has changed)
    @api.onchange('amount_company_currency')
    def _inverse_amount_company_currency(self):

        for rec in self:
            if rec.other_currency and rec.amount_company_currency != \
                    rec.currency_id._convert(
                        rec.amount, rec.company_id.currency_id,
                        rec.company_id, rec.date):
                force_amount_company_currency = rec.amount_company_currency
            else:
                force_amount_company_currency = False
            rec.force_amount_company_currency = force_amount_company_currency

    @api.depends('amount', 'other_currency', 'force_amount_company_currency', 'currency_id')
    def _compute_amount_company_currency(self):
        """
        * Si las monedas de deuda y pago son iguales, omite la conversión
        * Si no, aplica la conversión habitual usando `force_amount_company_currency` si está presente
        """
        for rec in self:
            if rec.currency_id == rec.company_currency_id:
                # Si la moneda de deuda y pago son iguales (ambos en VEF), no se realiza conversión
                rec.amount_company_currency = rec.amount
            elif not rec.other_currency:
                # Si no hay diferencia de moneda, usa el monto directo
                rec.amount_company_currency = rec.amount
            elif rec.force_amount_company_currency:
                # Si hay un monto forzado en la moneda de la compañía, úsalo
                rec.amount_company_currency = rec.force_amount_company_currency
            else:
                # Conversión regular para otras monedas
                rec.amount_company_currency = rec.currency_id._convert(
                    rec.amount, rec.company_currency_id, rec.company_id, rec.date
                )

    @api.model_create_multi
    def create(self, vals_list):
        """ If a payment is created from anywhere else we create the payment group in top """
        logging.info("ANTES DE CREAR")
        recs = super().create(vals_list)
        logging.info("DEPUES DE CREAR")
        if self._context.get('avoid_create_payment_group'):
            return recs
        for rec in recs.filtered(lambda x: not x.payment_group_id and not x.is_internal_transfer).with_context(
                created_automatically=True):
            if not rec.partner_id:
                raise ValidationError(_(
                    'Manual payments should not be created manually but created from Customer Receipts / Supplier Payments menus'))
            rec.payment_group_id = rec.env['account.payment.group'].create({
                'company_id': rec.company_id.id,
                'partner_type': rec.partner_type,
                'partner_id': rec.partner_id.id,
                'payment_date': rec.date,
                'communication': rec.ref,
            })
            rec.payment_group_id.post()
        return recs

    @api.depends('payment_group_id')
    def _compute_destination_account_id(self):
        """
        If we are paying a payment gorup with paylines, we use account
        of lines that are going to be paid
        """
        for rec in self:
            to_pay_account = rec.payment_group_id.to_pay_move_line_ids.mapped(
                'account_id')
            if len(to_pay_account) > 1:
                raise ValidationError(_(
                    'To Pay Lines must be of the same account!'))
            elif len(to_pay_account) == 1:
                rec.destination_account_id = to_pay_account[0]
            else:
                super(AccountPayment, rec)._compute_destination_account_id()

    def show_details(self):
        """
        Metodo para mostrar form editable de payment, principalmente para ser
        usado cuando hacemos ajustes y el payment group esta confirmado pero
        queremos editar una linea
        """
        return {
            'name': _('Payment Lines'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'python'
        'res_model': 'account.payment',
            'target': 'new',
            'res_id': self.id,
            'context': self._context,
        }

    def button_open_payment_group(self):
        self.ensure_one()
        return self.payment_group_id.get_formview_action()

    def _prepare_move_line_default_vals(self, write_off_line_vals=None, force_balance=None):
        res = super()._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals, force_balance=force_balance)
        if self.force_amount_company_currency:
            difference = self.force_amount_company_currency - res[0]['credit'] - res[0]['debit']
            if res[0]['credit']:
                liquidity_field = 'credit'
                counterpart_field = 'debit'
            else:
                liquidity_field = 'debit'
                counterpart_field = 'credit'
            res[0].update({
                liquidity_field: self.force_amount_company_currency,
            })
            res[1].update({
                counterpart_field: res[1][counterpart_field] + difference,
            })
        return res

    @api.model
    def _get_trigger_fields_to_sincronize(self):
        res = super()._get_trigger_fields_to_sincronize()
        return res + ('force_amount_company_currency',)

    @api.depends_context('default_is_internal_transfer')
    def _compute_is_internal_transfer(self):
        """ Este campo se recomputa cada vez que cambia un diario y queda en False porque el segundo diario no va a
        estar completado. Como nosotros tenemos un menú especifico para poder registrar las transferencias internas,
        entonces si estamos en este menu siempre es transferencia interna"""
        if self._context.get('default_is_internal_transfer'):
            self.is_internal_transfer = True
        else:
            return super()._compute_is_internal_transfer()

    def _create_paired_internal_transfer_payment(self):
        for rec in self:
            super(AccountPayment, rec.with_context(
                default_force_amount_company_currency=rec.force_amount_company_currency
            ))._create_paired_internal_transfer_payment()

    @api.onchange("payment_type")
    def _compute_label(self):
        for rec in self:
            if (rec.payment_type == "outbound"):
                rec.label_journal_id = "Diario de origen"
                rec.label_destination_journal_id = "Diario de destino"
            else:
                rec.label_journal_id = "Diario de destino"
                rec.label_destination_journal_id = "Diario de origen"
