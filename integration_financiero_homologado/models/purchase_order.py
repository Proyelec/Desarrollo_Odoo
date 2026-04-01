# /integration_financiero_homologado/models/purchase_order.py
from odoo import models, fields, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'integration.mixin']

    homologado_invoice_id = fields.Integer(
        string="ID Factura Destino",
        readonly=True,
        copy=False
    )

    def _prepare_homologado_purchase_data(self):
        """Prepara el diccionario de valores para enviar la Compra."""
        models_proxy, db, uid, password = self._get_remote_models_proxy()

        # Validación mínima local
        partner_identifier = self.partner_id.vat or getattr(self.partner_id, "rif", False) or getattr(self.partner_id, "identification_id", False)
        if not partner_identifier:
            raise UserError(_("El proveedor '%s' no tiene RIF/C.I/VAT configurado.") % self.partner_id.name)

        # ✅ AHORA: busca y si no existe, crea partner remoto
        partner_id_remoto = self._get_or_create_remote_partner(
            models_proxy, db, uid, password, self.partner_id
        )

        # Usuario fijo configurado para crear documentos en destino
        user_id_remoto = self._get_fixed_remote_user_id(
            models_proxy, db, uid, password
        )

        order_lines = []
        for line in self.order_line:
            # ✅ AHORA: busca y si no existe, crea producto remoto
            product_id_remoto = self._get_or_create_remote_product(
                models_proxy, db, uid, password, line.product_id
            )

            order_lines.append((0, 0, {
                'product_id': product_id_remoto,
                'name': line.name,
                'product_qty': line.product_qty,
                'price_unit': line.price_unit,
                'date_planned': line.date_planned.strftime('%Y-%m-%d %H:%M:%S') if line.date_planned else False,
            }))

        return {
            'partner_id': partner_id_remoto,
            'user_id': user_id_remoto,
            'date_order': fields.Datetime.to_string(self.date_order),
            'origin': self.name,
            'order_line': order_lines,
        }

    def action_send_to_homologado(self):
        """Prepara los datos y llama al método genérico con las acciones de Compra."""
        self.ensure_one()
        if self.homologado_id:
            raise UserError(
                _("Esta orden de compra ya fue enviada a la BD destino (ID: %s).")
                % self.homologado_id
            )

        vals = self._prepare_homologado_purchase_data()
        return self._action_send_to_homologado_generic(
            remote_model='purchase.order',
            vals=vals,
            confirm_method='button_confirm',
            invoice_method='action_create_invoice'
        )
