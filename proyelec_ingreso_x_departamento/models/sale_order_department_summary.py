from odoo import models, fields


class SaleOrderDepartmentSummary(models.Model):
    _name = "sale.order.department.summary"
    _description = "Resumen de Ingreso por Departamento"
    _order = "sale_order_id, departamento_id"

    sale_order_id = fields.Many2one(
        "sale.order",
        string="Pedido de Venta",
        required=True,
        ondelete="cascade",
        index=True,
    )
    departamento_id = fields.Many2one(
        "proyelec.departamento.medular",
        string="Departamento",
        required=True,
        ondelete="restrict",
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="sale_order_id.currency_id",
        store=True,
        string="Moneda",
    )
    total_venta = fields.Monetary(
        string="Total Venta",
        currency_field="currency_id",
    )
    porcentaje = fields.Float(
        string="% en este pedido",
        group_operator=False,
    )
    # Stored for grouping in pivot/graph without joins
    fecha = fields.Datetime(
        related="sale_order_id.date_order",
        string="Fecha",
        store=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        related="sale_order_id.partner_id",
        string="Cliente",
        store=True,
    )
