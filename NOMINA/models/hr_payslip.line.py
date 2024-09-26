from odoo import models, fields, api

class HrPayslipLineCustom(models.Model):
    _inherit = 'hr.payslip.line'

    total = fields.Float(string="Total", compute="_compute_total", store=True)
    total_ref = fields.Float(string="Total (REF)", compute="_compute_total_ref", store=True)

    @api.depends('amount')
    def _compute_total(self):
        for line in self:
            line.total = line.amount

    @api.depends('amount', 'slip_id.tasa_cambio')
    def _compute_total_ref(self):
        for line in self:
            tasa_cambio = line.slip_id.tasa_cambio if line.slip_id else 1.0
            line.total_ref = line.amount * tasa_cambio
