{
    "name": "Proyelec - SO to PO (Ganado)",
    "version": "17.0.1.0.0",
    "category": "Sales/Purchase",
    "summary": "Transfer selected won lines from Sales Order to Purchase Order with KPI tracking",
    "depends": ["sale_management", "purchase", "sale_margin"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/so_to_po_wizard_views.xml",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
