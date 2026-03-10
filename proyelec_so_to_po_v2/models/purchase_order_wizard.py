from odoo import api, models


class CreatePurchaseOrderGanado(models.TransientModel):
    _inherit = "create.purchaseorder"

    @api.model
    def default_get(self, default_fields):
        """
        Sobrescribe el default_get del wizard de BrowseInfo para incluir
        ÚNICAMENTE las líneas marcadas como Ganado (x_studio_ganado = True).

        Si ninguna línea está marcada como Ganado, se comporta igual que antes
        (pasa todas las líneas) para no bloquear el flujo existente.
        """
        res = super().default_get(default_fields)

        data = self.env["sale.order"].browse(self._context.get("active_ids", []))

        # Filtrar solo líneas ganadas
        ganado_lines = data.order_line.filtered(lambda l: l.x_studio_ganado)

        # Si no hay ninguna marcada, dejamos el wizard como está (comportamiento original)
        if not ganado_lines:
            return res

        # Reconstruir new_order_line_ids solo con las líneas ganadas
        update = []
        for record in ganado_lines:
            update.append((0, 0, {
                "product_id": record.product_id.id,
                "product_uom": record.product_uom.id,
                "order_id": record.order_id.id,
                "name": record.name,
                "product_qty": record.product_uom_qty,
                "price_unit": record.purchase_price or record.price_unit,
                "product_subtotal": record.price_subtotal,
            }))

        res["new_order_line_ids"] = update
        return res
