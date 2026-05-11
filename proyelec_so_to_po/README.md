# Proyelec - SO to PO (Won Lines)

**Version:** 17.0.1.0.0  
**Author:** AIT - Proyelec  
**License:** LGPL-3  
**Category:** Sales / Purchase

## Description

Extends the sales order confirmation flow so that procurement is only triggered for lines marked as **"Won"**, preventing purchase orders from being created for lines that were not awarded to the client.

## Features

- **"Won"** boolean field on each sale order line, indicating if the line was awarded
- On SO confirmation, only lines marked as Won trigger the stock rule and generate a purchase order
- **KPIs per SO:**
  - Total quoted lines
  - Won lines
  - Conversion rate (%)

## Installation

1. Copy the module into your Odoo addons directory
2. Update the module list
3. Install **Proyelec - SO to PO (Won Lines)**

## Dependencies

- `sale_management`
- `purchase`
- `sale_margin`
- `sale_stock`

## Usage

1. Create a sales quotation with multiple lines
2. Mark as **"Won"** the lines that were awarded to the client
3. On SO confirmation, only those lines will trigger procurement and generate purchase orders
