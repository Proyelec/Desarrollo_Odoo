from odoo import models, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_order_department_summary_ids = fields.One2many(
        "sale.order.department.summary",
        "sale_order_id",
        string="Resumen por Departamento",
        readonly=True,
    )

    def write(self, vals):
        # skip_departamento_check must be passed by automatic Odoo processes
        # (invoice creation, stock picking confirmation, scheduled actions)
        # to avoid blocking non-user-initiated writes on confirmed orders.
        if not self.env.context.get("skip_departamento_check"):
            confirming = vals.get("state") == "sale"
            for order in self:
                if order.state == "sale" or confirming:
                    unclassified = order.order_line.filtered(
                        lambda l: not l.display_type and not l.departamento_id
                    )
                    if unclassified:
                        names = []
                        for line in unclassified:
                            label = (
                                line.product_id.name
                                or line.name
                                or f"Línea #{line.sequence}"
                            )
                            names.append(label)
                        raise UserError(
                            "No se puede guardar el pedido en estado confirmado. "
                            "Las siguientes líneas no tienen departamento asignado:\n\n"
                            + "\n".join(f"• {n}" for n in names)
                        )
        return super().write(vals)

    def _recompute_department_summary(self):
        """Recalcula los registros de resumen por departamento para cada orden."""
        Summary = self.env["sale.order.department.summary"].sudo()
        for order in self:
            Summary.search([("sale_order_id", "=", order.id)]).unlink()
            dept_totals = {}
            for line in order.order_line:
                if line.display_type or not line.departamento_id:
                    continue
                dept_id = line.departamento_id.id
                dept_totals[dept_id] = dept_totals.get(dept_id, 0.0) + line.price_subtotal

            total_order = sum(dept_totals.values())
            for dept_id, total in dept_totals.items():
                Summary.create(
                    {
                        "sale_order_id": order.id,
                        "departamento_id": dept_id,
                        "total_venta": total,
                        "porcentaje": (total / total_order * 100) if total_order else 0.0,
                    }
                )
