# proyelec_ingreso_x_departamento — Revenue by Department

**Version:** 17.0.1.0.0  
**License:** LGPL-3  
**Depends on:** `sale_management`, `sale_margin`, `l10n_ve_dual_currency_bs`

---

## Overview

This module classifies sale order lines by **core department** (OPS / PCL) and provides an automatic revenue summary per department directly on the sale order. Only lines marked as **Won** (`x_studio_ganado`) are included in the summary totals.

---

## Features

### Department classification on order lines

A new `departamento_id` field is added to `sale.order.line`, linking to the `proyelec.departamento.medular` model. Users assign a department to each line; the field is required before a sale order can be confirmed.

### Core department catalog (`proyelec.departamento.medular`)

A lightweight master-data model with `name`, `code`, and `active` fields. Two departments are pre-seeded on installation: **OPS** and **PCL**.

### Automatic department summary

A `sale.order.department.summary` record is created for each department that has at least one won line on a given order. The summary stores:

| Field | Description |
|---|---|
| `departamento_id` | The department |
| `total_venta` | Sum of `price_subtotal` for won lines in this department |
| `porcentaje` | Percentage share of this department within the order's total won revenue |
| `fecha` | Order date (stored, for pivot/graph grouping) |
| `partner_id` | Customer (stored, for pivot/graph grouping) |

The summary is recalculated automatically whenever lines are created, updated, or deleted.

### Validation on confirm

When a sale order is saved in `sale` state, any product line without a department raises a `ValidationError` listing the unclassified lines by name.

---

## Models

| Model | Description |
|---|---|
| `proyelec.departamento.medular` | Core department master (OPS, PCL, …) |
| `sale.order.department.summary` | Per-order, per-department revenue summary |
| `sale.order.line` (extended) | Adds `departamento_id` |
| `sale.order` (extended) | Adds summary one2many + confirm validation |

---

## File Structure

```
proyelec_ingreso_x_departamento/
├── __manifest__.py
├── data/
│   └── departamento_medular_data.xml      # OPS and PCL seed data
├── models/
│   ├── departamento_medular.py
│   ├── sale_order.py
│   ├── sale_order_department_summary.py
│   └── sale_order_line.py
├── security/
│   └── ir.model.access.csv
└── views/
    ├── departamento_medular_views.xml
    ├── sale_order_views.xml               # Adds department column + summary tab
    └── sale_order_department_summary_views.xml
```

---

## Installation

```bash
# Install
odoo-bin -d YOUR_DB -i proyelec_ingreso_x_departamento --stop-after-init

# Update
odoo-bin -d YOUR_DB -u proyelec_ingreso_x_departamento --stop-after-init
```
