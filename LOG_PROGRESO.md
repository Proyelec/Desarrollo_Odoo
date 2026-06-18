# LOG PROGRESO — Desarrollo Odoo (AIT2)

## proyelec_ingreso_x_departamento — v1.0

**Sesión inicial**: 2026-06-18  
**Rama**: AIT2  
**Estado**: Implementado, pendiente prueba en AIT

---

### Decisiones técnicas tomadas

**1. Recompute del resumen (punto 4)**  
Elegido: `write()/create()/unlink()` en `sale.order.line` que llaman a `order_id._recompute_department_summary()`.  
Descartado: `@api.depends` en `sale.order` — requeriría que el resumen sea un campo computed, no un modelo propio, perdiendo la capacidad de agrupar por él en pivot/graph sin joins.  
El recompute usa `sudo()` porque el acceso de escritura al modelo `sale.order.department.summary` es solo para `base.group_system`.

**2. Validación write() — bypass context**  
Implementado en `sale.order.write()` con chequeo `self.env.context.get('skip_departamento_check')`.  
La validación dispara cuando `order.state == 'sale'` O `vals.get('state') == 'sale'` (cubre confirmación inicial Y ediciones posteriores).

**RIESGO IDENTIFICADO**: Odoo hace `write()` automático sobre `sale.order` al recalcular campos stored computados (`amount_total`, `invoice_status`) cuando cambian líneas. Esto ocurre dentro de la misma transacción del usuario pero sin el contexto bypass.  
- Si la SO confirmada tiene TODAS las líneas clasificadas → validación pasa sin problema  
- Si una SO OLD no tiene líneas clasificadas Y el usuario hace algo que dispara recalculo de campos stored → la validación bloqueará la operación  
- **Solución si ocurre**: agregar `with_context(skip_departamento_check=True)` en el método específico que esté bloqueando

**Procesos automáticos en este codebase (verificados)**:  
- `proyelec_so_to_po/_action_confirm()` → llama a `super()._action_confirm()` que hace `write({'state': 'sale', ...})` → queremos que valide (intencional, NO bypass)  
- `proyelec_so_to_po/_action_launch_stock_rule()` → escribe en procurement/stock, NO en `sale.order` directamente → sin riesgo  
- `l10n_ve_dual_currency_bs` → updates de tasa/moneda → escribe en `sale.order.line` campos bs, potencial riesgo si dispara stored compute en la orden → monitorear en pruebas

**3. Seguridad del catálogo departamentos**  
Sin grupo GDC en el sistema. Usado `base.group_system` para create/write/unlink. Vendedores (`base.group_user`) tienen solo lectura.

**4. Campo active_onchange**  
Definido en `l10n_ve_dual_currency_bs/models/sale_order.py:162` como Boolean en `sale.order.line`. La vista de ese módulo lo inserta antes de `price_unit`. Se ocultó con `invisible="1"` y se añadió `departamento_id` en su lugar. El módulo depende de `l10n_ve_dual_currency_bs` para garantizar el orden de aplicación de vistas.

**5. Porcentaje por período (punto 6)**  
No implementado como campo explícito. El pivot nativo de Odoo calcula sumas absolutas por departamento/período, desde donde GDC puede derivar visualmente el porcentaje. Si GDC pide el campo explícito, evaluar vista SQL (`_auto = False`).

**6. campo `fecha` en summary**  
Definido como `fields.Datetime` related a `sale_order_id.date_order` con `store=True`. Odoo lo mantiene automáticamente cuando cambia `date_order` en la SO.

---

### Estructura del módulo

```
proyelec_ingreso_x_departamento/
├── __init__.py
├── __manifest__.py
├── security/ir.model.access.csv
├── data/departamento_medular_data.xml
├── models/
│   ├── __init__.py
│   ├── departamento_medular.py       → proyelec.departamento.medular
│   ├── sale_order_department_summary.py → sale.order.department.summary
│   ├── sale_order_line.py            → herencia sale.order.line (campo + triggers)
│   └── sale_order.py                 → herencia sale.order (validación + recompute)
└── views/
    ├── departamento_medular_views.xml
    ├── sale_order_views.xml
    └── sale_order_department_summary_views.xml
```

---

### Checklist de prueba manual (pendiente)

- [ ] Instalar módulo → OPS/PCL creados automáticamente
- [ ] Crear SO nueva → columna Depto. visible en líneas
- [ ] Dejar línea sin depto., confirmar → UserError con nombres de líneas
- [ ] Clasificar todas las líneas, confirmar → pasa
- [ ] Editar SO confirmada (solo fecha entrega, todo clasificado) → pasa
- [ ] SO OLD sin departamentos: guardar → exige clasificar 100%
- [ ] Verificar que resumen muestra OPS/PCL con totales y porcentajes
- [ ] Verificar reporte pivot en Sales > Reporting > Ingresos por Departamento

---

### Patrones nuevos aprendidos

- `@api.model_create_multi` obligatorio en override de `create()` en Odoo 17  
- `column_invisible="1"` para ocultar columna en list sin `invisible`
- Vista embebida en one2many via `<list>` inline dentro del `<field>` en xpath — más limpio que referenciar xmlid
- `decoration-warning` en `<tree>` debe excluir secciones/notas: `not departamento_id and not display_type`
- Related stored fields (`fecha`, `partner_id`, `currency_id`) en summary se auto-calculan post-create — no pasarlos explícitamente al crear
