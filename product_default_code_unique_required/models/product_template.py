from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProductProduct(models.Model):
    _inherit = 'product.product'

    default_code = fields.Char(required=True, index=True)

    _sql_constraints = [
        ('default_code_uniq', 'unique(default_code)', 'El código interno debe ser único.')
    ]

    @api.constrains('default_code')
    def _check_default_code_not_empty(self):
        for product in self:
            if not product.default_code:
                raise ValidationError("El código interno es obligatorio.")

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('default_code')
    def _check_template_default_code_unique(self):
        for template in self:
            if template.default_code:
                existing = self.search([
                    ('default_code', '=', template.default_code),
                    ('id', '!=', template.id)
                ], limit=1)
                if existing:
                    raise ValidationError(
                        f"Ya existe un producto con el código interno '{template.default_code}'."
                    )