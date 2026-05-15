# LOG DE PROGRESO — AIT

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
