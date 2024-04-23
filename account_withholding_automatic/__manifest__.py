
{
    'name': 'Automatic Withholdings on Payments',
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
        'account_withholding',
        'account_payment_group',
    ],
    'data': [
        #'wizards/res_config_settings_views.xml',
        'views/account_tax_view.xml',
        'views/account_payment_group_view.xml',
        'views/account_payment_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': True,

}
