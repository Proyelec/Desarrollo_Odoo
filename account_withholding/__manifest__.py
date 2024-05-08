
{
    'name': 'Withholdings on Payment',
    'version': "17.0.1.2.0",
    'category': 'Accounting',
    'sequence': 14,
    'summary': '',
    'author': 'Jesus Pozzo',
    'website': '',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'account',
    ],
    'data': [
        'views/account_tax_view.xml',
        'views/account_payment_view.xml',
        #'views/account_journal_views.xml',
        'data/account_payment_method_data.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
