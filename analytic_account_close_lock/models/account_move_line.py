# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_closed_analytic_accounts(self, analytic_distribution):
        """
        Recibe un dict tipo {"12": 100, "34": 50} (analytic_distribution de Odoo 17),
        devuelve los recordset de cuentas analíticas cerradas que aparezcan en él.
        """
        if not isinstance(analytic_distribution, dict):
            return self.env["account.analytic.account"]

        analytic_ids = set()
        for key in analytic_distribution.keys():
            # Las keys pueden ser IDs simples "12" o combinadas "12,34"
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
                "No se puede guardar esta línea porque las siguientes cuentas analíticas "
                "están cerradas para imputación:\n\n%s\n\n"
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

    def write(self, vals):
        if "analytic_distribution" in vals:
            distribution = vals["analytic_distribution"]
            if distribution:
                closed = self._get_closed_analytic_accounts(distribution)
                self._raise_if_closed(closed)
        else:
            # Si no viene distribution en vals, validar la ya cargada en el registro
            # (para evitar que alguien modifique otro campo de una línea ya imputada
            # a una cuenta cerrada — evita ediciones silenciosas)
            for line in self:
                if line.analytic_distribution:
                    closed = self._get_closed_analytic_accounts(
                        line.analytic_distribution
                    )
                    self._raise_if_closed(closed)
        return super().write(vals)
