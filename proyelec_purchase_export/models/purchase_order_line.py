from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    x_analytic_display = fields.Char(
        string='Cuenta Analítica',
        compute='_compute_x_analytic_display',
        store=False,
    )

    @api.depends('analytic_distribution')
    def _compute_x_analytic_display(self):
        all_ids = set()
        for line in self:
            for key in (line.analytic_distribution or {}):
                for id_str in key.split(','):
                    id_str = id_str.strip()
                    if id_str.isdigit():
                        all_ids.add(int(id_str))

        accounts = {}
        if all_ids:
            records = self.env['account.analytic.account'].browse(list(all_ids)).exists()
            accounts = {rec.id: rec.name for rec in records}

        for line in self:
            dist = line.analytic_distribution or {}
            if not dist:
                line.x_analytic_display = False
                continue

            names = []
            for key in dist:
                for id_str in key.split(','):
                    id_str = id_str.strip()
                    if id_str.isdigit():
                        account_id = int(id_str)
                        name = accounts.get(account_id)
                        if name and name not in names:
                            names.append(name)

            line.x_analytic_display = ', '.join(names) if names else False
