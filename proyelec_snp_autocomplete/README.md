# proyelec_snp_autocomplete — SNP Internal Code Autocomplete

**Version:** 17.0.1.0.0  
**Author:** Juan David Villasmil — AIT Proyelec  
**License:** LGPL-3  
**Depends on:** `product`, `product_default_code_unique_required`

---

## Overview

Manages the sequential SNP internal code system for products. When a user types an SNP prefix (e.g., `TORSNP`) into the **Internal Reference** field, the system automatically completes it to the next available correlative (e.g., `TORSNP007`). It also validates format, detects gaps in the sequence, and handles bulk imports gracefully.

---

## SNP Code Format

```
[PREFIX]SNP[NUMBER]
```

| Part | Rule |
|---|---|
| `PREFIX` | 3 to 6 uppercase letters |
| `SNP` | Literal, uppercase |
| `NUMBER` | 1 to 4 digits |

**Valid examples:** `TORSNP001`, `CABSNP014`, `ABRSNP123`

---

## Layers of behavior

### Layer 0 — Bulk import autocreation

During a file import (`import_file` context), if a product row has no `default_code`, the system derives a prefix from the first three letters of the product name and assigns the next available SNP correlative automatically. The batch is handled atomically: correlatives assigned earlier in the same batch are taken into account to avoid duplicates.

### Layer 1 — Onchange autocomplete

If a user types only the prefix (e.g., `TORSNP`) without a number and leaves the field, the system fills in the next available correlative. Input is also normalized to uppercase automatically.

If a full SNP code is entered manually:
- A **warning** is shown if the number skips ahead of the last registered correlative (e.g., entering `TORSNP010` when the last is `TORSNP006`).
- The user can accept the out-of-sequence code, but the warning makes the gap explicit.

### Layer 2 — Format validation (`@constrains`)

On save, any `default_code` containing `SNP` that does not match the full SNP pattern raises a `ValidationError` with the expected format and examples.

### Layer 3 — Duplicate detection (`@constrains`)

On save, if the SNP code already exists on another product, a `ValidationError` is raised that includes the next available correlative as a suggestion.

All layers apply to both `product.template` and `product.product`.

---

## Interaction with `product_default_code_unique_required`

This module overrides the Boyer `_check_default_code_not_empty` constraint on `product.product` to allow empty `default_code` during file imports (Layer 0 fills it in before the constraint runs).

---

## File Structure

```
proyelec_snp_autocomplete/
├── __manifest__.py
├── models/
│   └── product_template.py   # ProductTemplate + ProductProduct extensions
└── views/
    └── product_template_views.xml
```

---

## Installation

```bash
# Install
odoo-bin -d YOUR_DB -i proyelec_snp_autocomplete --stop-after-init

# Update
odoo-bin -d YOUR_DB -u proyelec_snp_autocomplete --stop-after-init
```
