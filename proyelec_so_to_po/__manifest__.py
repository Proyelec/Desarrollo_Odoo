{
    "name": "Proyelec - SO to PO (Ganado)",
    "version": "17.0.1.0.0",
    "category": "Sales/Purchase",
    "summary": "Filtra líneas ganadas al confirmar SO para crear PO selectiva",
    "depends": ["sale_management", "purchase", "sale_margin", "sale_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}