# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _check_closed_analytic_account(self, account_id):
        if not account_id:
            return
        account = self.env["account.analytic.account"].browse(account_id).exists()
        if account and account.x_closed_for_posting:
            raise ValidationError(_(
                "No se puede crear ni modificar una imputación analítica sobre "
                "la cuenta '%s' porque está cerrada para imputación.\n\n"
                "Consulte con el responsable contable para reabrir la cuenta si es necesario."
            ) % account.name)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._check_closed_analytic_account(vals.get("account_id"))
        return super().create(vals_list)

    def write(self, vals):
        if "account_id" in vals:
            self._check_closed_analytic_account(vals["account_id"])
        else:
            # Validar que el registro existente no esté ya en una cuenta cerrada
            for rec in self:
                if rec.account_id and rec.account_id.x_closed_for_posting:
                    raise ValidationError(_(
                        "No se puede modificar esta línea analítica porque la cuenta '%s' "
                        "está cerrada para imputación.\n\n"
                        "Consulte con el responsable contable para reabrir la cuenta si es necesario."
                    ) % rec.account_id.name)
        return super().write(vals)
