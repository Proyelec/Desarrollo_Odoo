from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    x_studio_ganado = fields.Boolean(
        string="Ganado",
        default=False,
        copy=False,
        help="Indica que esta línea fue adjudicada al cliente.",
    )

    x_supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Proveedor",
        domain=[("supplier_rank", ">", 0)],
        help="Proveedor de esta línea. Determina el costo usado para calcular el margen.",
    )

    @api.depends("product_id", "company_id", "currency_id", "product_uom", "x_supplier_id", "x_studio_coste_1")
    def _compute_purchase_price(self):
        for line in self:
            if not line.product_id:
                line.purchase_price = 0.0
                continue
            # Si hay costo manual ingresado en x_studio_coste_1, usarlo
            if line.x_studio_coste_1:
                line.purchase_price = line.x_studio_coste_1
                continue
            # Si hay proveedor seleccionado, buscar su precio en supplierinfo
            if line.x_supplier_id:
                supplierinfo = self.env["product.supplierinfo"].search(
                    [
                        ("partner_id", "=", line.x_supplier_id.id),
                        "|",
                        ("product_id", "=", line.product_id.id),
                        ("product_tmpl_id", "=", line.product_id.product_tmpl_id.id),
                    ],
                    limit=1,
                )
                if supplierinfo:
                    line.purchase_price = supplierinfo.price
                    continue
            # Comportamiento estándar de Odoo
            line = line.with_company(line.company_id)
            product_cost = line.product_id.uom_id._compute_price(
                line.product_id.standard_price,
                line.product_uom,
            )
            line.purchase_price = line._convert_to_sol_currency(
                product_cost,
                line.product_id.cost_currency_id,
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
        return super(SaleOrder, self).with_context(skip_procurement=True)._action_confirm()
