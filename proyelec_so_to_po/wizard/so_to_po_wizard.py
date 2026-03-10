from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SoToPoWizardLine(models.TransientModel):
    _name = "proyelec.so.to.po.wizard.line"
    _description = "Línea del wizard SO → PO"

    wizard_id = fields.Many2one("proyelec.so.to.po.wizard", required=True, ondelete="cascade")
    sale_line_id = fields.Many2one("sale.order.line", string="Línea de Venta", readonly=True)
    product_id = fields.Many2one(related="sale_line_id.product_id", string="Producto", readonly=True)
    product_qty = fields.Float(related="sale_line_id.product_uom_qty", string="Cantidad", readonly=True)
    price_unit = fields.Float(
        related="sale_line_id.purchase_price",
        string="Costo unitario",
        readonly=True,
    )
    selected = fields.Boolean(string="Incluir", default=True)


class SoToPoWizard(models.TransientModel):
    _name = "proyelec.so.to.po.wizard"
    _description = "Wizard: Transferir líneas Ganado a OC"

    sale_order_id = fields.Many2one("sale.order", string="Orden de Venta", readonly=True)
    partner_id = fields.Many2one(
        "res.partner",
        string="Proveedor",
        required=True,
        domain=[("supplier_rank", ">", 0)],
    )
    line_ids = fields.One2many(
        "proyelec.so.to.po.wizard.line",
        "wizard_id",
        string="Líneas a transferir",
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        sale_id = self.env.context.get("default_sale_order_id")
        if sale_id:
            sale = self.env["sale.order"].browse(sale_id)
            ganado_lines = sale.order_line.filtered(
                lambda l: l.x_studio_ganado and not l.x_po_transferred
            )
            res["line_ids"] = [
                (0, 0, {"sale_line_id": line.id, "selected": True})
                for line in ganado_lines
            ]
        return res

    def action_create_po(self):
        self.ensure_one()
        selected_lines = self.line_ids.filtered("selected")
        if not selected_lines:
            raise UserError(_("Selecciona al menos una línea para transferir."))

        # Create or find draft PO for this vendor
        PO = self.env["purchase.order"]
        po = PO.search([
            ("partner_id", "=", self.partner_id.id),
            ("state", "=", "draft"),
            ("origin", "like", self.sale_order_id.name),
        ], limit=1)

        if not po:
            po = PO.create({
                "partner_id": self.partner_id.id,
                "origin": self.sale_order_id.name,
            })

        # Add lines to PO
        POLine = self.env["purchase.order.line"]
        for wiz_line in selected_lines:
            sol = wiz_line.sale_line_id
            po_line = POLine.create({
                "order_id": po.id,
                "product_id": sol.product_id.id,
                "name": sol.name or sol.product_id.name,
                "product_qty": sol.product_uom_qty,
                "product_uom": sol.product_uom.id,
                "price_unit": sol.purchase_price or 0.0,
                "date_planned": fields.Datetime.now(),
            })
            # Mark the sale line as transferred and link it
            sol.write({
                "x_po_transferred": True,
                "x_po_line_id": po_line.id,
            })

        # Notification + open the PO
        return {
            "type": "ir.actions.act_window",
            "name": "Orden de Compra",
            "res_model": "purchase.order",
            "res_id": po.id,
            "view_mode": "form",
            "target": "current",
        }
