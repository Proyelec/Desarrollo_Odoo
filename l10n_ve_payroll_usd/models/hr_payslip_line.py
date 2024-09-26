# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HRPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    currency_id_dif = fields.Many2one("res.currency", string="Referencia en Divisa", default=lambda self: self.env.company.currency_id_dif)
    total_ref = fields.Monetary(store=True, readonly=True, compute="_total_ref", string="Total (REF)", default=0,
                                currency_field='currency_id_dif')
    total = fields.Monetary(string='Total', compute='_compute_totals', store=True)

    dias = fields.Char(compute='_compute_dias', store=True, string="Días")
    horas = fields.Char(compute='_compute_dias', store=True, string="Horas")

    department_id = fields.Many2one('hr.department', string='Departamento', related='employee_id.department_id', store=True)

    struct_id = fields.Many2one('hr.payroll.structure', string='Estructura', related='slip_id.struct_id', store=True)

    @api.depends('total', 'slip_id.tasa_cambio')
    def _total_ref(self):
        # tax_today_id = self.env['res.currency'].search([('name', '=', 'USD')])
        for record in self:
            if record.slip_id.tasa_cambio > 0:
                record[("total_ref")] = round(record.amount * record.slip_id.tasa_cambio, 2)
            else:
                record[("total_ref")] = 0
            
            record.total = record.amount


    @api.depends('name','total_ref', 'salary_rule_id')
    def _compute_dias(self):
        valor_dias = ""
        valor_horas = ""
        for rec in self:
            worked_days_line_ids = rec.slip_id.worked_days_line_ids
            if rec.category_id.code == 'BASIC':
                valor_dias = worked_days_line_ids.filtered(lambda x: x.code == 'WORK100').number_of_days + worked_days_line_ids.filtered(lambda x: x.code == 'AUSEP').number_of_days
            else:
                worked_days_line_ids = rec.slip_id.worked_days_line_ids.filtered(lambda x: x.code == rec.code)
                if rec.salary_rule_id.mostrar_cantidad == 'dias':
                    if len(worked_days_line_ids) > 0:
                        valor_dias = round(worked_days_line_ids.number_of_days,2)
                    else:
                        valor_dias = ""
                    valor_horas = ""
                elif rec.salary_rule_id.mostrar_cantidad == 'horas':
                    if len(worked_days_line_ids) > 0:
                        valor_horas = round(worked_days_line_ids.number_of_hours,2)
                    else:
                        valor_horas = ""
                    valor_dias = ""
                else:
                    valor_dias = ""
                    valor_horas = ""

            rec.dias = str(valor_dias)
            rec.horas = str(valor_horas)
