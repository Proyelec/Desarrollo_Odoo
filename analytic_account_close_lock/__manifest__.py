# -*- coding: utf-8 -*-
{
    "name": "Analytic Account Close Lock",
    "version": "17.0.1.0.0",
    "summary": "Bloquea nuevas imputaciones en cuentas analíticas cerradas",
    "description": """
        Permite marcar una cuenta analítica como 'Cerrada para imputación'.
        Una vez cerrada:
        - No se pueden crear ni modificar líneas de factura/asiento que la usen.
        - No se pueden crear ni modificar líneas analíticas directas sobre ella.
        - Solo el grupo 'Analytic Close Manager' puede cerrar o reabrir cuentas.
        - Se registra quién cerró la cuenta y en qué fecha.
    """,
    "category": "Accounting/Accounting",
    "author": "Juan Villasmil",
    "license": "LGPL-3",
    "depends": [
        "account",
        "analytic",
    ],
    "data": [
        "security/analytic_close_security.xml",
        "security/ir.model.access.csv",
        "views/account_analytic_account_views.xml",
    ],
    "installable": True,
    "application": False,
}
