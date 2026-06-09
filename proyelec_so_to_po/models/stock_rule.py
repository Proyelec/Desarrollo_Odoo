import logging
from odoo import models

_logger = logging.getLogger(__name__)


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, values, po):
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, po
        )
        sale_line_id = values.get('sale_line_id')
        # LOG TEMPORAL — confirmar tipo antes de quitar
        _logger.warning(
            '[proyelec_so_to_po] sale_line_id type=%s value=%r',
            type(sale_line_id).__name__,
            sale_line_id,
        )
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
