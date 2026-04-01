# /integration_financiero_homologado/models/sale_order.py
from odoo import models, fields, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'integration.mixin']

    homologado_invoice_id = fields.Integer(
        string="ID Factura Destino",
        readonly=True,
        copy=False
    )

    def _prepare_homologado_sale_data(self):
        """Prepara el diccionario de valores para enviar la Venta."""
        models_proxy, db, uid, password = self._get_remote_models_proxy()

        # Validación mínima local
        partner_identifier = self.partner_id.vat or getattr(self.partner_id, "rif", False) or getattr(self.partner_id, "identification_id", False)
        if not partner_identifier:
            raise UserError(_("El cliente '%s' no tiene RIF/C.I/VAT configurado.") % self.partner_id.name)

        # ✅ AHORA: busca y si no existe, crea partner remoto
        partner_id_remoto = self._get_or_create_remote_partner(
            models_proxy, db, uid, password, self.partner_id
        )

        # Usuario fijo configurado para crear documentos en destino
        user_id_remoto = self._get_fixed_remote_user_id(
            models_proxy, db, uid, password
        )

        order_lines = []
        for line in self.order_line.filtered(lambda l: not l.display_type):
            # ✅ AHORA: busca y si no existe, crea producto remoto
            product_id_remoto = self._get_or_create_remote_product(
                models_proxy, db, uid, password, line.product_id
            )

            order_lines.append((0, 0, {
                'product_id': product_id_remoto,
                'product_uom_qty': line.product_uom_qty,
                'price_unit': line.price_unit,
            }))

        return {
            'partner_id': partner_id_remoto,
            'user_id': user_id_remoto,
            'date_order': fields.Datetime.to_string(self.date_order),
            'origin': self.name,
            'order_line': order_lines,
        }

    def action_send_to_homologado(self):
        """Prepara los datos y llama al método genérico con las acciones de Venta."""
        self.ensure_one()
        if self.homologado_id:
            raise UserError(
                _("Este pedido ya fue enviado a la BD destino (ID: %s).")
                % self.homologado_id
            )

        vals = self._prepare_homologado_sale_data()
        return self._action_send_to_homologado_generic(
            remote_model='sale.order',
            vals=vals,
            confirm_method='action_confirm',
            invoice_method='action_create_invoice_wizard'  # simbólico
        )
