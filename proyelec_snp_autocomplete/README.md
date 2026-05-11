# Proyelec SNP Autocomplete

**Version:** 17.0.1.0.0  
**Author:** AIT - Proyelec  
**License:** LGPL-3  
**Category:** Inventory

## Description

Automates the assignment of SNP-format internal reference codes on products. When the user types an SNP prefix (e.g. `TORSNP`), the system detects the last used correlative and automatically fills in the next available one. Also validates the format and warns if a manually entered correlative is out of sequence.

## SNP Format

```
[PREFIX]SNP[NNN]
```

- **PREFIX:** 3 to 6 uppercase letters (e.g. `TOR`, `CAB`, `ABR`)
- **SNP:** literal uppercase
- **NNN:** 1 to 4 digits

**Valid examples:** `TORSNP006`, `CABSNP014`, `ABRSNP123`

## Features

- **Autocomplete:** typing only the prefix (e.g. `TORSNP`) auto-fills the next available correlative
- **Format validation:** blocks saving if the SNP code does not meet the required format
- **Duplicate detection:** intercepts Odoo's native message and shows the next available correlative when a duplicate is detected
- **Sequence alert:** warns if a manually entered correlative skips positions relative to the last registered one

## Installation

1. Copy the module into your Odoo addons directory
2. Update the module list
3. Install **Proyelec SNP Autocomplete**

## Dependencies

- `product`
- `product_default_code_unique_required`
