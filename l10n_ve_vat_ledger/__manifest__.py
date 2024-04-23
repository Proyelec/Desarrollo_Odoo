###############################################################################
# 
# Copyleft: 2023-Present.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
#
#Jesus Pozzo
###############################################################################


{
    'name': "Localización Vat Ledger Venezuela",
    'description': """
|           Libros de Compras y ventas.
    """,
    'author': "Jesús Pozzo",
    'website': "",
    'category': 'Localization',
    "version": "17.0.1.0.0",
    'depends': [
        'account', 
        'l10n_ve_base',
        'l10n_ve_withholding', 
        'xlsx_reporting', 
        'l10n_ve_igtf_purchase',
        'l10n_ve_dual_currency_bs'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_vat_ledger_views.xml',
        'wizard/account_wizard_views.xml',
        'report/account_vat_ledger_report.xml',
    ],

}

