# proyelec_so_to_po — SO to PO (Won Lines Only)

**Version:** 17.0.1.1.0  
**License:** LGPL-3  
**Depends on:** `sale_management`, `purchase`, `sale_margin`, `sale_stock`, `purchase_stock`, `bi_convert_purchase_from_sales`

---

## Overview

Extends the Sale-to-Purchase flow so that only sale order lines explicitly marked as **Won** (`x_studio_ganado`) are processed when confirming a sale order. Non-won lines are excluded from stock procurement and purchase order generation. The module also tracks line-level conversion KPIs and propagates analytic distributions from SO lines to the resulting PO lines.

---

## Features

### Won flag on sale order lines

A `x_studio_ganado` (Won) boolean field is added to `sale.order.line`. It defaults to `False`. Users tick this checkbox on the lines that were actually awarded before confirming the order.

### Confirm guard

Confirming a sale order raises a `UserError` if no lines are marked as Won.

### Selective stock procurement

On confirmation, the standard blanket `_action_launch_stock_rule()` call (which would process all lines) is suppressed via `skip_procurement` context. Only the won lines then trigger their own stock rules. Non-won lines remain on the order but do not generate pickings or purchase requisitions.

### Analytic distribution propagation

When `bi_convert_purchase_from_sales` creates a PO line from a SO line, the `analytic_distribution` from the originating SO line is copied to the PO line automatically.

### Conversion KPIs

Three computed fields are added to `sale.order`:

| Field | Description |
|---|---|
| `x_kpi_total_lines` | Total number of order lines |
| `x_kpi_ganado_lines` | Number of lines marked as Won |
| `x_kpi_conversion_rate` | Won lines / total lines × 100 (stored) |
| `x_kpi_conversion_label` | Human-readable `"N/M"` format |

### KPI pie chart view

A **KPI Conversión de Líneas** action is added to the Sales → Reports menu. It displays a pie chart of `sale.order.line` records grouped by Won / Pending status, scoped to confirmed orders, with date filters for today, this month, and this year.

---

## Models Extended

| Model | Changes |
|---|---|
| `sale.order.line` | Adds `x_studio_ganado`, `x_kpi_estado_ganado` |
| `sale.order` | Adds KPI fields, overrides `_action_confirm` |
| `purchase.order.line` | Overrides `_prepare_purchase_order_line_from_procurement` to copy analytic distribution |

---

## File Structure

```
proyelec_so_to_po/
├── __manifest__.py
├── models/
│   ├── sale_order.py           # Won flag, KPIs, confirm override
│   └── purchase_order_line.py  # Analytic distribution propagation
├── security/
│   └── ir.model.access.csv
└── views/
    ├── sale_order_views.xml    # Won checkbox column on SO line tree
    └── kpi_conversion_views.xml  # Pie chart + menu item
```

---

## Installation

```bash
# Install
odoo-bin -d YOUR_DB -i proyelec_so_to_po --stop-after-init

# Update
odoo-bin -d YOUR_DB -u proyelec_so_to_po --stop-after-init
```
