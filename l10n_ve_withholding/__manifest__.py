

{
    'name': 'Localización Withholding Venezuela',
    'description': """
        **Localización VENEZUELA Withholding**

        ¡Felicidades!. Este es el módulo Withholding para la implementación de
        la **Localización Venezuela** que agrega características y datos
        necesarios para un correcto ejercicio fiscal de su empresa.
    """,
    'version': "17.0.1.2.0",
    'category': 'Accounting',
    'summary': '',
    'author': 'Jesus Pozzo',
    'website': '',
    'license': 'AGPL-3',
    'images': [
    ],
    'depends': [
        'account', 'l10n_ve_base','account_withholding_automatic','account_payment_group','l10n_ve_dual_currency_bs'
    ],
    'data': [
        'data/account_tax_withholding_template.xml',
        'data/seniat_factor.xml',
        'data/seniat_partner_type.xml',
        'data/seniat_ut.xml',
        'data/seniat_tabla_islr.xml',
        'data/account_move_sequence.xml',
        'reports/report_templates.xml',
        'reports/report_withholding_certificate.xml',
        'reports/report_withholding_certificate_iva.xml',
        'reports/report_payment_group.xml',
       'views/account_payment_view.xml',
        'views/res_partner_view.xml',
        'security/ir.model.access.csv',
        'views/account_journal_view.xml',
        'views/account_move_view.xml',
        'views/seniat_ut_view.xml',
        'views/seniat_factor_view.xml',
        'views/seniat_partner_type_view.xml',
        'views/seniat_tabla_islr_view.xml',
        'views/account_payment_group_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
}
