from odoo import api, models, fields


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    departamento_id = fields.Many2one(
        "proyelec.departamento.medular",
        string="Departamento",
        ondelete="restrict",
    )

    def write(self, vals):
        result = super().write(vals)
        recompute_triggers = {
            "departamento_id",
            "price_subtotal",
            "product_uom_qty",
            "price_unit",
            "discount",
            "tax_id",
            "product_id",
            "x_studio_ganado",
        }
        if recompute_triggers.intersection(vals.keys()):
            self.mapped("order_id")._recompute_department_summary()
        return result

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.mapped("order_id")._recompute_department_summary()
        return records

    def unlink(self):
        orders = self.mapped("order_id")
        result = super().unlink()
        orders._recompute_department_summary()
        return result
