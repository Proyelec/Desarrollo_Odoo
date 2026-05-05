# -*- coding: utf-8 -*-
{
    "name": "Analytic Account Close Lock",
    "version": "17.0.1.0.0",
    "summary": "Bloquea nuevas imputaciones en cuentas analiticas cerradas",
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
