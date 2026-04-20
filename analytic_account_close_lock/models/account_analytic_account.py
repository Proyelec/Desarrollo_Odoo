# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    x_closed_for_posting = fields.Boolean(
        string="Cerrada para imputación",
        default=False,
        copy=False,
        help="Si está marcada, no se podrán crear ni modificar imputaciones analíticas "
             "sobre esta cuenta. Solo el grupo 'Analytic Close Manager' puede cambiar este estado.",
    )
    x_closed_date = fields.Date(
        string="Fecha de cierre",
        readonly=True,
        copy=False,
        help="Fecha en que se cerró la cuenta analítica para nuevas imputaciones.",
    )
    x_closed_by = fields.Many2one(
        comodel_name="res.users",
        string="Cerrada por",
        readonly=True,
        copy=False,
        help="Usuario que marcó esta cuenta como cerrada.",
    )

    def _check_close_manager_group(self):
        """Verifica que el usuario pertenezca al grupo Analytic Close Manager."""
        group = self.env.ref(
            "analytic_account_close_lock.group_analytic_close_manager",
            raise_if_not_found=False,
        )
        if group and self.env.user not in group.users:
            raise AccessError(_(
                "Solo los usuarios del grupo 'Analytic Close Manager' pueden "
                "cerrar o reabrir cuentas analíticas."
            ))

    def write(self, vals):
        # Si se intenta cambiar el estado de cierre, verificar grupo
        if "x_closed_for_posting" in vals:
            self._check_close_manager_group()

            if vals["x_closed_for_posting"]:
                # Cerrando: registrar fecha y usuario
                vals["x_closed_date"] = fields.Date.today()
                vals["x_closed_by"] = self.env.user.id
            else:
                # Reabriendo: limpiar fecha y usuario
                vals["x_closed_date"] = False
                vals["x_closed_by"] = False

        return super().write(vals)
