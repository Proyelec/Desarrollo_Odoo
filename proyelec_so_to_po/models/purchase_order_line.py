from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_purchase_order_line_from_procurement(self, product_id, product_qty, product_uom, company_id, values, po):
        res = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        sale_line_id = values.get('sale_line_id')
        if not sale_line_id:
            return res
        if isinstance(sale_line_id, models.BaseModel):
            sale_line = sale_line_id
        else:
            sale_line = self.env['sale.order.line'].browse(sale_line_id)
        analytic = getattr(sale_line, 'analytic_distribution', None)
        if analytic:
            res['analytic_distribution'] = analytic
        return res
