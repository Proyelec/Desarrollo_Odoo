import re
from odoo import models, api
from odoo.exceptions import ValidationError


# Patrón válido completo: 3-6 letras mayúsculas + SNP + 1-4 dígitos
SNP_COMPLETO = re.compile(r'^([A-Z]{3,6}SNP)(\d{1,4})$')

# Patrón de trigger (solo prefijo, sin número): TORSNP
SNP_TRIGGER = re.compile(r'^[A-Z]{3,6}SNP$')


def _calcular_maximo_snp(env, prefijo, excluir_template_id=None, excluir_product_id=None):
    """
    Función auxiliar global — calcula el correlativo máximo existente
    para un prefijo dado, buscando en product.product directamente.
    Excluye el registro actual para no contarse a sí mismo.
    """
    dominio = [('default_code', 'like', prefijo)]
    if excluir_product_id:
        dominio.append(('id', '!=', excluir_product_id))
    elif excluir_template_id:
        dominio.append(('product_tmpl_id', '!=', excluir_template_id))

    existentes = env['product.product'].search(dominio)
    maximos = []
    for prod in existentes:
        m = SNP_COMPLETO.match(prod.default_code or '')
        if m and m.group(1) == prefijo:
            maximos.append(int(m.group(2)))

    return max(maximos) if maximos else None


def _calcular_siguiente_snp(env, prefijo, excluir_template_id=None, excluir_product_id=None):
    """
    Función auxiliar global — retorna el siguiente correlativo disponible
    para un prefijo dado, en formato PREFIJO + NNN (zfill 3).
    """
    maximo = _calcular_maximo_snp(
        env, prefijo,
        excluir_template_id=excluir_template_id,
        excluir_product_id=excluir_product_id,
    )
    siguiente = (maximo + 1) if maximo is not None else 1
    return f'{prefijo}{str(siguiente).zfill(3)}'


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # ------------------------------------------------------------------
    # CAPA 1 — Autocompletado (onchange)
    # Trigger: usuario escribe "TORSNP" y sale del campo (Tab/clic)
    # Acción:  sugiere el siguiente correlativo disponible (max + 1)
    # ------------------------------------------------------------------
    @api.onchange('default_code')
    def _onchange_default_code_snp(self):
        codigo = (self.default_code or '').strip().upper()

        # Normalizar a mayúsculas
        if self.default_code and self.default_code != codigo:
            self.default_code = codigo

        # --- Trigger de autocompletado ---
        if SNP_TRIGGER.match(codigo):
            siguiente = _calcular_siguiente_snp(
                self.env, codigo,
                excluir_template_id=self.id or None,
            )
            self.default_code = siguiente
            return

        # --- Warning por correlativo fuera de secuencia ---
        m = SNP_COMPLETO.match(codigo)
        if m:
            prefijo = m.group(1)
            numero = int(m.group(2))
            maximo = _calcular_maximo_snp(
                self.env, prefijo,
                excluir_template_id=self.id or None,
            )

            if maximo is None:
                if numero != 1:
                    siguiente_str = f'{prefijo}001'
                    return {
                        'warning': {
                            'title': 'Correlativo fuera de secuencia',
                            'message': (
                                f"No existen productos con el prefijo '{prefijo}'.\n"
                                f"El primer correlativo debe ser {siguiente_str}.\n\n"
                                f"Código ingresado: {codigo}\n"
                                f"Código sugerido:  {siguiente_str}\n\n"
                                f"Puede continuar, pero se recomienda usar el correlativo sugerido."
                            ),
                        }
                    }
            else:
                esperado = maximo + 1
                if numero > esperado:
                    siguiente_str = f'{prefijo}{str(esperado).zfill(3)}'
                    salto = numero - esperado
                    return {
                        'warning': {
                            'title': 'Correlativo fuera de secuencia',
                            'message': (
                                f"El correlativo ingresado ({codigo}) salta {salto} "
                                f"posición(es) respecto al último registrado.\n\n"
                                f"Último correlativo: {prefijo}{str(maximo).zfill(3)}\n"
                                f"Siguiente sugerido: {siguiente_str}\n\n"
                                f"Puede continuar, pero se recomienda usar el correlativo sugerido."
                            ),
                        }
                    }

    # ------------------------------------------------------------------
    # CAPA 2 — Validación de formato (constrains)
    # Bloquea códigos SNP con formato inválido al momento de guardar.
    # ------------------------------------------------------------------
    @api.constrains('default_code')
    def _check_snp_formato(self):
        for template in self:
            codigo = template.default_code or ''
            if 'SNP' not in codigo.upper():
                continue
            if not SNP_COMPLETO.match(codigo):
                raise ValidationError(
                    f"El código '{codigo}' no cumple el formato SNP requerido.\n\n"
                    f"Formato correcto: [PREFIJO]SNP[NNN]\n"
                    f"  - Prefijo: entre 3 y 6 letras mayúsculas\n"
                    f"  - SNP: literal en mayúsculas\n"
                    f"  - Número: entre 1 y 4 dígitos\n\n"
                    f"Ejemplos válidos: TORSNP006, CABSNP014, ABRSNP123"
                )

    # ------------------------------------------------------------------
    # CAPA 3 — Detección de duplicado con sugerencia (constrains)
    # Corre antes que Boyer e incluye el siguiente correlativo sugerido.
    # ------------------------------------------------------------------
    @api.constrains('default_code')
    def _check_snp_duplicado(self):
        for template in self:
            codigo = template.default_code or ''
            m = SNP_COMPLETO.match(codigo)
            if not m:
                continue

            dominio = [('default_code', '=', codigo)]
            if template.id:
                dominio.append(('id', '!=', template.id))

            duplicado = self.env['product.template'].search(dominio, limit=1)
            if duplicado:
                prefijo = m.group(1)
                siguiente = _calcular_siguiente_snp(
                    self.env, prefijo,
                    excluir_template_id=template.id or None,
                )
                raise ValidationError(
                    f"El código '{codigo}' ya está en uso.\n\n"
                    f"El siguiente correlativo disponible es: {siguiente}"
                )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # ------------------------------------------------------------------
    # CAPA 3 en product.product — intercepta ANTES del _sql_constraints
    # de Boyer, tanto al presionar Enter como al guardar manualmente.
    # ------------------------------------------------------------------
    @api.constrains('default_code')
    def _check_snp_duplicado_variant(self):
        for product in self:
            codigo = product.default_code or ''
            m = SNP_COMPLETO.match(codigo)
            if not m:
                continue

            dominio = [('default_code', '=', codigo)]
            if product.id:
                dominio.append(('id', '!=', product.id))

            duplicado = self.env['product.product'].search(dominio, limit=1)
            if duplicado:
                prefijo = m.group(1)
                siguiente = _calcular_siguiente_snp(
                    self.env, prefijo,
                    excluir_product_id=product.id or None,
                )
                raise ValidationError(
                    f"El código '{codigo}' ya está en uso.\n\n"
                    f"El siguiente correlativo disponible es: {siguiente}"
                )