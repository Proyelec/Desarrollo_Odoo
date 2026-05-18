# LOG DE PROGRESO — AIT

## Sesión 2026-05-18

- **Qué cambió:** Fix en `proyelec_so_to_po` — `_action_confirm` ahora usa `skip_procurement=True` al llamar al `super()` para suprimir la llamada masiva de `sale_stock` que lanzaba stock rules a TODAS las líneas, luego dispara `_action_launch_stock_rule()` manualmente solo sobre líneas con `x_studio_ganado=True`
- **Verificado en AIT:** SO S02187 confirmado con 1 línea ganada (CABSNP007) y 1 no-ganada (V-500-711-1); solo se generó P02178 para CABSNP007; la línea no-ganada no produjo PO — comportamiento correcto
- **Pendiente:** Limpiar SOs de prueba (S02186, S02187) y POs (P02176–P02178) en AIT; `proyelec_so_to_po` queda pendiente de merge a main

## Sesión 2026-05-15

- **Qué cambió:** Verificación funcional de `proyelec_snp_autocomplete` en AIT — no se modificó código, solo pruebas en UI
- **Verificado:** Trigger SNP funciona correctamente (`TORSNP` + Tab → autocompleta a `TORSNP010`, último en BD era TORSNP009); warning de correlativo fuera de secuencia dispara correctamente (`TORSNP050` → "salta 40 posiciones, sugerido: TORSNP010"); el campo `default_code` aparece etiquetado como "Número de Parte" en el formulario de producto
- **Pendiente:** Sigue abierto: métodos duplicados `@api.onchange('default_code')` en `ProductTemplate` (líneas 84 y 146 de `product_template.py`); issues de `proyelec_so_to_po` (`digits` deprecated y lógica `_action_confirm`)

## Sesión 2026-05-14

- **Qué cambió:** Fix completo en `proyelec_chatter_fix` — parche JS corregido (retorno era objeto no array) + Python fuerza `active=False` en el store JS para usuarios archivados que entran por historial de mensajes sin el campo `active`
- **Bug encontrado:** `mail_message.py:974` carga autores de mensajes sin `active` → `partner.active = undefined` en JS → `=== false` no capturaba archivados; además el parche JS anterior usaba `Array.isArray` sobre un objeto y nunca ejecutaba el filtro
- **Pendiente:** Validar en AIT que Chantal/Rafael/Nestor/Jessica desaparecen de sugerencias @; resolver issues del audit de rama (proyelec_snp_autocomplete métodos duplicados, proyelec_so_to_po digits deprecated y lógica `_action_confirm`)

## Sesión 2026-05-13

- **Qué cambió:** Configuración inicial del agente — instalación de Claude Code, SSH a Odoo.sh AIT, creación de CLAUDE.md
- **Bugs/Limitaciones:** Ninguno — setup limpio
- **Pendiente:** Crear script proxy BD, continuar con proyelec_calendar_personal
