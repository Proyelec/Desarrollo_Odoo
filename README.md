# Odoo 17 - Proyelec Custom Modules

Custom modules developed by the Proyelec AIT team for Odoo 17.

**Lead Developer:** Juan Villasmil ([@jdvillasmil](https://github.com/jdvillasmil))

---

## Available Modules

### 🔒 analytic_account_close_lock
Closes analytic accounts to block new postings. Only users in the **Analytic Close Manager** group can open or close accounts. Records closing date and user automatically.  
→ [View README](./analytic_account_close_lock/README.md)

---

### 💬 proyelec_chatter_fix
Fixes `@mention` suggestions in the Chatter by filtering out archived internal users so they no longer appear in the mention list.  
→ [View README](./proyelec_chatter_fix/README.md)

---

### 📅 proyelec_calendar_personal
Syncs room bookings with each user's personal calendar, allowing meeting room reservations to appear directly in Odoo's standard calendar view.  
→ [View README](./proyelec_calendar_personal/README.md)

---

### 📊 proyelec_procura_kpi
Effectiveness KPI for tasks in the PROCURA project. Displays the percentage of won lines over quoted lines as a progress bar in list view and a badge in kanban view.  
→ [View README](./proyelec_procura_kpi/README.md)

---

### 🏢 proyelec_salas
Meeting room booking module with privacy controls, attendee management, gantt view, automatic reminders, and calendar synchronization.  
→ [View README](./proyelec_salas/README.md)

---

### 👤 proyelec_sale_createdby
Adds a **"Created By"** column with user avatar to the Sales Quotations list view. Optional and read-only column.  
→ [View README](./proyelec_sale_createdby/README.md)

---

### 🔢 proyelec_snp_autocomplete
Autocomplete and validation for SNP-format internal reference codes on products. Typing the prefix (e.g. `TORSNP`) automatically suggests the next available correlative and validates the format on save.  
→ [View README](./proyelec_snp_autocomplete/README.md)

---

### 🔄 proyelec_so_to_po
Filters procurement on SO confirmation so only lines marked as **"Won"** generate purchase orders. Includes conversion rate KPIs per quotation.  
→ [View README](./proyelec_so_to_po/README.md)

---

## General Installation

1. Copy the desired modules into your Odoo addons directory
2. Restart the Odoo server
3. Go to **Settings → Activate Developer Mode**
4. Go to **Apps → Update Apps List**
5. Search and install each module

## Odoo Version

All modules are developed and tested on **Odoo 17.0 Community/Enterprise**.
