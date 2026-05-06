from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # x_studio_ganado is already created by Studio (Boolean field)
    # We add computed helpers for KPI display

    x_po_transferred = fields.Boolean(
        string="Transferido a OC",
        default=False,
        copy=False,
        help="Indica que esta línea ya fue transferida a una Orden de Compra.",
    )
    x_po_line_id = fields.Many2one(
        "purchase.order.line",
        string="Línea OC vinculada",
        readonly=True,
        copy=False,
    )


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # ── KPI fields ──────────────────────────────────────────────────────────
    x_kpi_total_lines = fields.Integer(
        string="Total líneas cotizadas",
        compute="_compute_kpi",
        store=False,
    )
    x_kpi_ganado_lines = fields.Integer(
        string="Líneas ganadas",
        compute="_compute_kpi",
        store=False,
    )
    x_kpi_transferred_lines = fields.Integer(
        string="Líneas transferidas a OC",
        compute="_compute_kpi",
        store=False,
    )
    x_kpi_conversion_rate = fields.Float(
        string="Tasa de conversión (%)",
        compute="_compute_kpi",
        store=False,
        digits=(5, 2),
    )

    @api.depends("order_line", "order_line.x_studio_ganado", "order_line.x_po_transferred")
    def _compute_kpi(self):
        for order in self:
            lines = order.order_line
            total = len(lines)
            ganado = len(lines.filtered("x_studio_ganado"))
            transferred = len(lines.filtered("x_po_transferred"))
            order.x_kpi_total_lines = total
            order.x_kpi_ganado_lines = ganado
            order.x_kpi_transferred_lines = transferred
            order.x_kpi_conversion_rate = (ganado / total * 100) if total else 0.0

    def action_open_so_to_po_wizard(self):
        """Open wizard to transfer won lines to a Purchase Order."""
        self.ensure_one()
        ganado_lines = self.order_line.filtered(
            lambda l: l.x_studio_ganado and not l.x_po_transferred
        )
        if not ganado_lines:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Sin líneas disponibles",
                    "message": "No hay líneas marcadas como Ganado pendientes de transferir.",
                    "type": "warning",
                    "sticky": False,
                },
            }
        return {
            "type": "ir.actions.act_window",
            "name": "Transferir a Orden de Compra",
            "res_model": "proyelec.so.to.po.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_sale_order_id": self.id,
            },
        }
