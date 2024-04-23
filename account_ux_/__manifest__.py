# © 2016 ADHOC SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account UX',
    "version": "17.0.1.0.0",
    "category": "Accounting",
    "website": "www.adhoc.com.ar",
    "author": "ADHOC SA, AITIC S.A.S",
    "license": "AGPL-3",
    'auto_install': True,
    'application': False,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        'account',
        "base_vat",
        "account_debit_note",
    ],
    "data": [
     'security/account_ux_security.xml',
        'security/ir.model.access.csv',
        'wizards/account_change_currency_views.xml',
        'wizards/res_config_settings_views.xml',
        'views/account_journal_views.xml',
        'views/account_move_line_views.xml',
        'views/account_reconcile_views.xml',
        'views/res_partner_views.xml',
        'views/account_partial_reconcile_views.xml',
        'views/account_account_views.xml',
        'views/account_move_views.xml',
    ],
    "demo": [
    ],
}

