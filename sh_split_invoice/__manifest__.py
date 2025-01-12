# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Split Accounting",
    "author": "Softhealer Technologies",
    "website": "http://www.softhealer.com",
    "support": "support@softhealer.com",
    "license": "OPL-1",
    "category": "Accounting",
    "summary": "Split Invoices Split Bills Split Credit Notes Split Debit Notes Extract Invoices Extract Bills Extract Credit Notes Extract Debit Notes Exttract Accounting Split Invoice Split Bill Split Credit Note Split Debit Note Extract Invoice Extract Bill Extract Credit Note Extract Debit Note Odoo Invoice Splitting Invoices Splitting Customer Invoice Separation Split Customer Invoices Split Vendor Bills Divide Invoices Invoice Splitting App Split Invoice Line Splitting Split Invoice Lines",
    "description": """Split function helpful to split selected order lines and create new invoice/bill/credit note/debit note and remove selected lines from the existing invoice/bill/credit note/debit note. In the split function, you have 2 options, new & existing. Extract function helpful to extract order lines without removing from the existing invoice/bill/credit note/debit note. We have added a checkbox in product lines so it will help you to decide which item you want to split/extract. Whatever ticked products will go in the wizard for split/extract who is in the "Draft" state. If you don't tick then it will add all items in the wizard.""",
    "version": "0.0.1",
    "depends": [
        "account",
    ],
    "application": True,
    "data": [
        "security/split_invoice_security_groups.xml",
        "security/ir.model.access.csv",
        "views/account_move_views.xml",
        "views/res_config_settings_views.xml",
        "wizard/split_invoice_wizard_views.xml",
    ],
    "images": [
        "static/description/background.png",
    ],
    "auto_install": False,
    "installable": True,
    "price": 20,
    "currency": "EUR",
}
