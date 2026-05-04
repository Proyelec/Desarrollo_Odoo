import re
from odoo import models, api
from odoo.exceptions import ValidationError


# Patrón válido completo: 3-6 letras mayúsculas + SNP + 1-4 dígitos
SNP_COMPLETO = re.compile(r'^([A-Z]{3,6}SNP)(\d{1,4})$')

# Patrón de trigger (solo prefijo, sin número): TORSNP
SNP_TRIGGER = re.compile(r'^[A-Z]{3,6}SNP$')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # ------------------------------------------------------------------
    # CAPA 1 — Autocompletado (onchange)
    # ------------------------------------------------------------------
    @api.onchange('default_code')
    def _onchange_default_code_snp(self):
        codigo = (self.default_code or '').strip().upper()

        # Normalizar a mayúsculas
        if self.default_code and self.default_code != codigo:
            self.default_code = codigo

        # --- Trigger de autocompletado ---
        if SNP_TRIGGER.match(codigo):
            siguiente = self._snp_siguiente_correlativo(codigo)
            self.default_code = siguiente
            return

        # --- Trigger de warning por correlativo fuera de secuencia ---
        m = SNP_COMPLETO.match(codigo)
        if m:
            prefijo = m.group(1)
            numero = int(m.group(2))
            maximo = self._snp_maximo_existente(prefijo)

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
    # CAPA 3 — Detección de duplicado SNP con sugerencia (constrains)
    # Complementa el constraint de Boyer agregando el correlativo sugerido
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
                siguiente = self._snp_siguiente_correlativo(prefijo)
                raise ValidationError(
                    f"El código '{codigo}' ya está en uso.\n\n"
                    f"El siguiente correlativo disponible es: {siguiente}"
                )

    # ------------------------------------------------------------------
    # Métodos auxiliares privados
    # ------------------------------------------------------------------
    def _snp_maximo_existente(self, prefijo):
        dominio = [('default_code', 'like', prefijo)]
        if self.id:
            dominio.append(('id', '!=', self.id))

        existentes = self.env['product.template'].search(dominio)
        maximos = []
        for prod in existentes:
            m = SNP_COMPLETO.match(prod.default_code or '')
            if m and m.group(1) == prefijo:
                maximos.append(int(m.group(2)))

        return max(maximos) if maximos else None

    def _snp_siguiente_correlativo(self, prefijo):
        maximo = self._snp_maximo_existente(prefijo)
        siguiente = (maximo + 1) if maximo is not None else 1
        return f'{prefijo}{str(siguiente).zfill(3)}'