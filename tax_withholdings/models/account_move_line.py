
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class AccountMoveLineWithHoldings(models.Model):
    _inherit = "account.move.line"

    tsc_cod_retencion_islr = fields.Char(string="ISLR withholding code")

    @api.constrains('account_id', 'move_id')
    def _check_company_consistency(self):
        for line in self:
            # Verificar que las empresas de la cuenta y el movimiento sean consistentes
            if line.move_id and line.account_id and line.account_id.company_id != line.move_id.company_id:
                raise ValidationError(_("La empresa de la cuenta contable y el diario no coinciden para la línea contable %s.") % line.name)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Asegurar que company_id se herede del movimiento si no está definido
            if 'move_id' in vals and 'company_id' not in vals:
                move = self.env['account.move'].browse(vals['move_id'])
                vals['company_id'] = move.company_id.id if move else False
        return super(AccountMoveLineWithHoldings, self).create(vals_list)

    def write(self, vals):
        if 'account_id' in vals:
            account = self.env['account.account'].browse(vals['account_id'])
            for line in self:
                # Verificar que las empresas sean consistentes al cambiar la cuenta
                if line.move_id and account.company_id != line.move_id.company_id:
                    raise ValidationError(_("No puede cambiar a una cuenta con una empresa diferente en la línea contable %s.") % line.name)
        return super(AccountMoveLineWithHoldings, self).write(vals)
