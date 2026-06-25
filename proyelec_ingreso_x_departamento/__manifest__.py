{
    "name": "Proyelec - Ingreso por Departamento",
    "version": "17.0.1.0.0",
    "category": "Sales",
    "summary": "Clasifica líneas de pedido de venta por departamento medular (OPS/PCL) y consolida ingresos",
    "depends": [
        "sale_management",
        "sale_margin",
        "l10n_ve_dual_currency_bs",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/departamento_medular_data.xml",
        "views/departamento_medular_views.xml",
        "views/sale_order_views.xml",
        "views/sale_order_department_summary_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
