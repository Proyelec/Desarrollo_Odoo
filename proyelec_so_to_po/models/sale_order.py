from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    x_studio_ganado = fields.Boolean(
        string="Ganado",
        default=False,
        copy=False,
        help="Indica que esta línea fue adjudicada al cliente.",
    )


class SaleOrder(models.Model):
    _inherit = "sale.order"

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
    x_kpi_conversion_rate = fields.Float(
        string="Tasa de conversión (%)",
        compute="_compute_kpi",
        store=False,
        digits=(5, 2),
    )

    @api.depends("order_line", "order_line.x_studio_ganado")
    def _compute_kpi(self):
        for order in self:
            lines = order.order_line
            total = len(lines)
            ganado = len(lines.filtered("x_studio_ganado"))
            order.x_kpi_total_lines = total
            order.x_kpi_ganado_lines = ganado
            order.x_kpi_conversion_rate = (ganado / total * 100) if total else 0.0

    def _action_confirm(self):
        """Solo lanza procurement para líneas marcadas como Ganado."""
        ganado_lines = self.order_line.filtered(lambda l: l.x_studio_ganado)
        if ganado_lines:
            ganado_lines._action_launch_stock_rule()
        return super(SaleOrder, self.with_context(skip_procurement=True))._action_confirm()