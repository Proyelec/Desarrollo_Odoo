
{
    'name': 'Account UX',
    'version': "17.0.1.2.0",
    'category': 'Accounting',
    'sequence': 14,
    'summary': '',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'account',
        "base_vat",
        "account_debit_note",
    ],
    'data': [
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
        'views/account_payment_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    # lo hacemos auto install porque este repo no lo podemos agregar en otros
    # por build de travis (ej sipreco) y queremos que para runbot se auto
    # instale
    'auto_install': True,
    'application': False,
}
