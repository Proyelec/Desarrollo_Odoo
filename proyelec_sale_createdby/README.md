# proyelec_sale_createdby — Created By Column in Quotations

**Version:** 17.0.1.0.0  
**Author:** Juan David Villasmil — AIT Proyelec  
**License:** LGPL-3  
**Depends on:** `sale`

---

## Overview

Adds a **Created By** column to the Quotations/Sales Orders list view, showing the user who originally created each record. The column is optional (shown by default) and uses Odoo's avatar widget for a visual display.

---

## What it adds

A view inheritance on `sale.sale_order_tree` inserts the `create_uid` field immediately after the existing `user_id` (Salesperson) column:

| Field | Widget | Optional | Read-only |
|---|---|---|---|
| `create_uid` (Creado por) | `many2one_avatar_user` | Yes (shown) | Yes |

No Python models are added or modified — this is a pure view change.

---

## File Structure

```
proyelec_sale_createdby/
├── __manifest__.py
└── views/
    └── sale_order_views.xml
```

---

## Installation

```bash
# Install
odoo-bin -d YOUR_DB -i proyelec_sale_createdby --stop-after-init

# Update
odoo-bin -d YOUR_DB -u proyelec_sale_createdby --stop-after-init
```
