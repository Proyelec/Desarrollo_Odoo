# analytic_account_close_lock

**Version:** 17.0.1.0.0  
**Author:** Juan Villasmil  
**License:** LGPL-3  
**Depends on:** `account`, `analytic`

---

## Overview

This module lets accounting managers lock analytic accounts against new postings. Once an analytic account is marked as closed, no new analytic lines or journal item distributions can be created or modified against it. A dedicated security group controls who can open and close accounts.

---

## Features

### Closed-state flag on analytic accounts

Three new fields are added to `account.analytic.account`:

| Field | Type | Description |
|---|---|---|
| `x_closed_for_posting` | Boolean | When `True`, the account is locked. Default: `False`. |
| `x_closed_date` | Date | Set automatically to today when the account is closed. Read-only. |
| `x_closed_by` | Many2one → `res.users` | The user who closed the account. Read-only. |

Toggling `x_closed_for_posting` back to `False` clears both `x_closed_date` and `x_closed_by`.

### Access control for toggling

Only users in the **Analytic Close Manager** group (under the Accounting category) may change the `x_closed_for_posting` flag. Any attempt by a non-member raises an `AccessError`.

### Block on analytic lines (`account.analytic.line`)

- **Create:** each line in a multi-create batch is checked; posting to a closed account raises a `ValidationError`.
- **Write:** if `account_id` is being changed, the target account is validated. If the account is not being changed but the existing account is already closed, the write is also blocked.

### Block on journal item analytic distribution (`account.move.line`)

The `analytic_distribution` field stores a JSON dict whose keys are comma-separated analytic account ID strings. On **create**, each line is inspected and any closed account referenced in the distribution raises a `ValidationError` listing all offending account names.

### Form view changes

- A yellow **warning banner** appears at the top of the analytic account form when `x_closed_for_posting` is `True`, showing the closure date and the responsible user.
- A new **"Analytic Close Control"** group section is added to the form with a boolean toggle.
- The list view gains optional columns for the closed flag, closure date, and user.

---

## Security Groups

| Group | XML ID | Description |
|---|---|---|
| Analytic Close Manager | `analytic_account_close_lock.group_analytic_close_manager` | Can close and reopen analytic accounts. |

Assign this group to accounting managers from **Settings → Users**.

---

## File Structure

```
analytic_account_close_lock/
├── __manifest__.py
├── models/
│   ├── account_analytic_account.py   # New fields + write guard
│   ├── account_analytic_line.py      # Create/write guard on analytic lines
│   └── account_move_line.py          # Create guard on journal item distributions
├── security/
│   ├── analytic_close_security.xml   # Group definition
│   └── ir.model.access.csv
└── views/
    └── account_analytic_account_views.xml  # Form/list view inheritance
```

---

## Installation

```bash
# Install
odoo-bin -d YOUR_DB -i analytic_account_close_lock --stop-after-init

# Update
odoo-bin -d YOUR_DB -u analytic_account_close_lock --stop-after-init
```
