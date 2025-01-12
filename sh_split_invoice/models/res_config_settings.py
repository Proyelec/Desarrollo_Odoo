
from odoo import fields, models


class ResCompanyPurchasesArchive(models.Model):
    _inherit = 'res.company'

    sh_invoice_remove_qty = fields.Boolean(
        'Remove Splitted quantity from Invoice/Bill/Credit Note/Debit Note', default=True, readonly=False)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_invoice_remove_qty = fields.Boolean(
        'Remove Splitted quantity from Invoice/Bill/Credit Note/Debit Note', related="company_id.sh_invoice_remove_qty", readonly=False)
