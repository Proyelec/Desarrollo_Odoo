# Desarrollo_Odoo — Módulos Personalizados Odoo 17

Repositorio oficial de módulos Odoo 17 desarrollados por **AIT Proyelec** para **Proyelec International C.A.**

---

## Contexto

Proyelec opera sobre Odoo 17 en Odoo.sh, con un proveedor principal (**Contables Boyer**) que gestiona los módulos fiscales venezolanos (retenciones, conciliación bancaria, reportes fiscales). Este repositorio contiene módulos desarrollados de forma independiente por el equipo de AIT Proyelec para cubrir necesidades operativas específicas, sin interferir con los módulos de Boyer.

**Entorno de desarrollo:** Rama staging `Test7` en Odoo.sh (`proyelec-test7-26614961`)  
**Módulos personalizados en servidor:** `/home/odoo/src/user/`  
**Comandos de instalación:** `odoo-bin -d proyelec-test7-26614961 -c /etc/odoo/odoo.conf -i nombre_modulo --stop-after-init`  
**Comando de actualización:** `odoo-update nombre_modulo`

---

## Principios de Desarrollo

- **Herencia sobre reescritura** — Todos los módulos usan `_inherit` para extender modelos existentes, nunca se reescriben.
- **Intervenciones quirúrgicas** — Cada módulo modifica únicamente lo necesario, sin afectar funcionalidades globales.
- **Patrones correctos de Odoo 17** — Sin parámetros deprecados (`states`, `track_visibility`, `digits` en fields).
- **Límite claro con Boyer** — No se tocan módulos de contabilidad fiscal venezolana. Todo lo que involucre retenciones, conciliación o reportes fiscales queda bajo responsabilidad de Contables Boyer.

---

## Módulos

### `proyelec_chatter_fix`

**Propósito:** Corrección del comportamiento del chatter en el modelo `res.partner`.

**Problema que resuelve:** El chatter en ciertas vistas de contactos no mostraba correctamente el historial de mensajes y seguimiento.

**Solución técnica:** Herencia del modelo `res.partner` con ajuste quirúrgico en la lógica de visualización del chatter, sin modificar el módulo base de mensajería.

**Dependencias:** `mail`  
**Afecta:** `res.partner`  
**Riesgo:** Bajo

---

### `proyelec_so_to_po`

**Propósito:** Asistente (wizard) para convertir líneas de una Orden de Venta (SO) en una Orden de Compra (PO).

**Problema que resuelve:** El proceso manual de trasladar ítems cotizados desde una SO a una PO era propenso a errores y consumía tiempo. Además, Boyer utiliza un módulo de terceros que transfiere todas las líneas de la SO sin filtrar, lo que generaba ruido operativo.

**Solución técnica:**
- Wizard heredado que lee las líneas de la SO activa
- Filtra únicamente las líneas marcadas como ganadas (`x_studio_ganado = True`)
- Genera la PO con los proveedores, precios y cantidades correspondientes
- Incluye reglas de seguridad y vistas propias

**Dependencias:** `sale_margin`, `purchase`  
**Afecta:** `sale.order`, wizard de conversión  
**Riesgo:** Medio — requiere que el campo `x_studio_ganado` esté presente (creado por Studio)

---

### `proyelec_so_to_po_v2`

**Propósito:** Versión refactorizada del módulo `proyelec_so_to_po`.

**Mejoras sobre v1:**
- Implementación más limpia usando el modelo `purchase_order_wizard`
- Mejor manejo de casos borde (líneas sin proveedor, precios en cero)
- Código más mantenible y documentado

**Estado:** Versión activa en uso. La v1 se mantiene en el repositorio como referencia histórica.

**Dependencias:** `sale_margin`, `purchase`  
**Afecta:** `sale.order`, wizard de conversión  
**Riesgo:** Medio

---

### `proyelec_procura_kpi`

**Propósito:** Campo computado de KPI de efectividad de renglones para el proyecto PROCURA.

**Problema que resuelve:** El proyecto PROCURA maneja 4 propiedades de tareas (Renglones Ofertados, Solicitados, Fuera de Tiempo y Ganados) almacenadas como campo JSON dinámico (`task_properties`). Este tipo de campo no es filtrable ni ordenable en la interfaz estándar de Odoo. Adicionalmente, la gerencia necesitaba un indicador de efectividad visible directamente en las vistas.

**Solución técnica:**
- Campo `x_kpi_efectividad` (Float, `store=True`) computado automáticamente
- Fórmula: `(Renglones Ganados / Renglones Ofertados) * 100`
- Lee directamente del dict `task_properties` usando los hashes de cada propiedad
- Solo aplica a tareas del proyecto PROCURA (`project_id = 1019`)
- Vista lista: columna con widget `progressbar` (opcional, visible por defecto)
- Vista kanban: badge verde con el porcentaje cuando KPI > 0
- Vista search: filtro rápido "Con Renglones (PROCURA)"

**Hashes de propiedades PROCURA** (definidos en `task_properties_definition`):

| Propiedad | Hash |
|---|---|
| Renglones Ofertados | `d586b6ea5f215286` |
| Renglones Fuera de Tiempo | `22ad07ba6464c583` |
| Renglones Solicitados | `07c5531119478422` |
| Renglones Ganados | `38a0d51c237f9082` |

**⚠️ Consideración para producción:** El `PROCURA_PROJECT_ID = 1019` está hardcodeado para el ambiente de staging. Verificar el ID del proyecto en producción antes del pase y actualizar la constante en `models/project_task.py`.

**Dependencias:** `project`  
**Afecta:** `project.task` (solo proyecto PROCURA)  
**Riesgo:** Bajo

---

## Estructura del Repositorio

```
Desarrollo_Odoo/
├── README.md
├── proyelec_chatter_fix/
│   ├── __init__.py
│   ├── __manifest__.py
│   └── models/
│       ├── __init__.py
│       └── res_partner.py
├── proyelec_so_to_po/
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   ├── security/
│   ├── views/
│   └── wizard/
├── proyelec_so_to_po_v2/
│   ├── __init__.py
│   ├── __manifest__.py
│   └── models/
└── proyelec_procura_kpi/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init__.py
    │   └── project_task.py
    └── views/
        └── project_task_views.xml
```

---

## Instalación en Nuevo Ambiente

1. Copiar el módulo deseado a `/home/odoo/src/user/` en el servidor Odoo.sh
2. Instalar:
```bash
odoo-bin -d NOMBRE_DB -c /etc/odoo/odoo.conf -i nombre_modulo --stop-after-init
```
3. Para actualizar después de cambios:
```bash
odoo-update nombre_modulo
```

---

## Consideraciones para Pase a Producción

- Coordinar con Contables Boyer para verificar que ningún módulo interfiera con sus desarrollos fiscales
- Verificar IDs hardcodeados (especialmente `PROCURA_PROJECT_ID` en `proyelec_procura_kpi`)
- Confirmar que los campos Studio referenciados (`x_studio_ganado`) existen en el ambiente de producción
- Ejecutar instalación en horario de bajo tráfico

---

## Equipo

**Desarrollador:** Juan Villasmil — AIT Proyelec  
**Cliente:** Proyelec International C.A.  
**Proveedor Odoo:** Contables Boyer (módulos fiscales venezolanos)
