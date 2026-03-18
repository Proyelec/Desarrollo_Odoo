# odoo17-custom-modules

Custom Odoo 17 modules developed for production environments running on Odoo.sh.

Each module follows Odoo 17 best practices: model inheritance over rewriting, no deprecated parameters, surgical interventions that avoid touching unrelated functionality.

---

## Development Environment

- **Platform:** Odoo.sh
- **Version:** Odoo 17
- **Custom modules path:** `/home/odoo/src/user/`
- **Install:** `odoo-bin -d <database> -c /etc/odoo/odoo.conf -i <module_name> --stop-after-init`
- **Update:** `odoo-update <module_name>`

---

## Modules

### `analytic_account_close_lock`

**Purpose:** Adds a "Closed for Posting" flag to analytic accounts to prevent new imputations after a project or period has been formally closed and reported.

**Problem solved:** In standard Odoo 17, there is no native way to block new analytic imputations on a per-account basis once a project is closed and its report has been submitted. Lock Dates only protect by accounting date, not by analytic account status.

**Technical solution:**
- Boolean field `x_closed_for_posting` on `account.analytic.account`
- `ValidationError` raised on `account.move.line` (invoices, bills, journal entries) and `account.analytic.line` (timesheets, expenses) if the target analytic account is closed
- Handles both simple and compound keys in `analytic_distribution` dict (Odoo 17 format)
- Records closure date (`x_closed_date`) and responsible user (`x_closed_by`) automatically
- Warning banner displayed on the analytic account form when closed
- Security group `Analytic Close Manager` — only members can close or reopen accounts

**Dependencies:** `account`, `analytic`
**Affects:** `account.analytic.account`, `account.move.line`, `account.analytic.line`
**Risk:** Low

---

### `proyelec_chatter_fix`

**Purpose:** Fixes chatter behavior on the `res.partner` model.

**Problem solved:** The chatter in certain contact views was not correctly displaying message history and tracking.

**Technical solution:** Minimal inheritance of `res.partner` with a targeted fix on chatter display logic, without modifying the base messaging module.

**Dependencies:** `mail`
**Affects:** `res.partner`
**Risk:** Low

---

### `proyelec_so_to_po`

**Purpose:** Wizard to convert selected Sale Order lines into a Purchase Order.

**Problem solved:** The manual process of transferring quoted items from an SO to a PO was error-prone. Available third-party solutions transferred all lines indiscriminately without filtering.

**Technical solution:**
- Wizard that reads active SO lines
- Filters only lines marked as won (`x_studio_ganado = True`)
- Generates a PO with the corresponding vendors, prices and quantities
- Includes access rules and dedicated views

**Dependencies:** `sale_margin`, `purchase`
**Affects:** `sale.order`, conversion wizard
**Risk:** Medium — requires `x_studio_ganado` field created via Studio

---

### `proyelec_so_to_po_v2`

**Purpose:** Refactored version of `proyelec_so_to_po`.

**Improvements over v1:**
- Cleaner implementation using `purchase_order_wizard` model
- Better handling of edge cases (lines without vendor, zero prices)
- More maintainable and documented code

**Status:** Active version in use. v1 kept for historical reference.

**Dependencies:** `sale_margin`, `purchase`
**Affects:** `sale.order`, conversion wizard
**Risk:** Medium

---

### `proyelec_procura_kpi`

**Purpose:** Computed KPI field for bid line effectiveness on a specific project.

**Problem solved:** Project task properties stored as a dynamic JSON field (`task_properties`) are not filterable or sortable in Odoo's standard interface. Management needed a visible effectiveness indicator directly in task views.

**Technical solution:**
- Computed field `x_kpi_efectividad` (Float, `store=True`)
- Formula: `(Won Lines / Offered Lines) * 100`
- Reads directly from `task_properties` dict using property hashes
- Scoped to a specific project via `PROCURA_PROJECT_ID` constant
- List view: progress bar column (optional, visible by default)
- Kanban view: green badge when KPI > 0
- Search view: quick filter for tasks with lines

**⚠️ Note for new environments:** `PROCURA_PROJECT_ID` in `models/project_task.py` is hardcoded for the staging database. Verify and update the project ID before deploying to a different environment.

**Dependencies:** `project`
**Affects:** `project.task` (scoped to one project)
**Risk:** Low

---

## Repository Structure

```
odoo17-custom-modules/
├── README.md
├── analytic_account_close_lock/
│   ├── __init__.py
│   ├── __manifest__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── account_analytic_account.py
│   │   ├── account_analytic_line.py
│   │   └── account_move_line.py
│   ├── security/
│   │   ├── analytic_close_security.xml
│   │   └── ir.model.access.csv
│   └── views/
│       └── account_analytic_account_views.xml
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

## Installation

1. Copy the desired module to `/home/odoo/src/user/` on the Odoo.sh server
2. Install:
```bash
odoo-bin -d <database> -c /etc/odoo/odoo.conf -i <module_name> --stop-after-init
```
3. Update after changes:
```bash
odoo-update <module_name>
```

---

## Development Principles

- **Inheritance over rewriting** — All modules use `_inherit` to extend existing models
- **Surgical changes** — Each module only modifies what is strictly necessary
- **Odoo 17 patterns** — No deprecated parameters (`states`, `track_visibility`, `digits` on fields)
- **Tested on Odoo.sh staging** before any production deployment

---

## Author

Juan Villasmil — Odoo Developer