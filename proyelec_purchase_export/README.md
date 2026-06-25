# proyelec_purchase_export — Purchase Order Analytic Export

**Version:** 17.0.1.0.0  
**License:** LGPL-3  
**Depends on:** `purchase`, `analytic`

---

## Overview

Odoo stores analytic distributions on purchase order lines as a JSON dictionary keyed by analytic account IDs. This makes exported spreadsheets unreadable. This module adds a computed, human-readable field that resolves those IDs to account names, making it available for export.

---

## What it adds

A single computed field is added to `purchase.order.line`:

| Field | Type | Description |
|---|---|---|
| `x_analytic_display` | Char | Comma-separated list of analytic account names derived from `analytic_distribution`. |

The field is marked `exportable=True` so it appears in the column selector when exporting purchase orders to Excel or CSV. It is not stored in the database (`store=False`).

### How it works

The field reads `analytic_distribution` (a `{key: percentage}` dict where keys may be comma-separated ID strings), collects all unique account IDs, fetches their names in a single query, and joins the distinct names with `, `.

---

## File Structure

```
proyelec_purchase_export/
├── __manifest__.py
├── models/
│   └── purchase_order_line.py   # Adds x_analytic_display
└── security/
    └── ir.model.access.csv
```

---

## Installation

```bash
# Install
odoo-bin -d YOUR_DB -i proyelec_purchase_export --stop-after-init

# Update
odoo-bin -d YOUR_DB -u proyelec_purchase_export --stop-after-init
```

After installation, open any purchase order, switch to list view, and use **Action → Export** to see the new **Cuenta Analítica** column available for selection.
