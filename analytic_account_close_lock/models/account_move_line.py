# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_closed_analytic_accounts(self, analytic_distribution):
        if not isinstance(analytic_distribution, dict):
            return self.env["account.analytic.account"]
        analytic_ids = set()
        for key in analytic_distribution.keys():
            for part in str(key).split(","):
                part = part.strip()
                if part.isdigit():
                    analytic_ids.add(int(part))
        if not analytic_ids:
            return self.env["account.analytic.account"]
        return self.env["account.analytic.account"].browse(
            list(analytic_ids)
        ).filtered(lambda a: a.x_closed_for_posting)

    def _raise_if_closed(self, closed_accounts):
        if closed_accounts:
            names = ", ".join(closed_accounts.mapped("name"))
            raise ValidationError(_(
                "No se puede guardar esta linea porque las siguientes cuentas analiticas "
                "estan cerradas para imputacion:\n\n%s\n\n"
                "Consulte con el responsable contable para reabrir la cuenta si es necesario."
            ) % names)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            distribution = vals.get("analytic_distribution")
            if distribution:
                closed = self._get_closed_analytic_accounts(distribution)
                self._raise_if_closed(closed)
        return super().create(vals_list)
