# -*- coding: utf-8 -*-
from odoo import api, models

class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    @api.model
    def get_entry_types(self, payslip):
    
        entry_types = {
        
            'WORK100': [entry for entry in payslip.worked_days_line_ids if entry.code == 'WORK100'],
            'AUSE': [entry for entry in payslip.worked_days_line_ids if entry.code == 'AUSE'],
            'AUSEP': [entry for entry in payslip.worked_days_line_ids if entry.code == 'AUSEP'],
            'VACA': [entry for entry in payslip.worked_days_line_ids if entry.code == 'VACA'],
            'DDFVACA': [entry for entry in payslip.worked_days_line_ids if entry.code == 'DDFVACA'],
            'DDESS': [entry for entry in payslip.worked_days_line_ids if entry.code == 'DDESS'],
            'DDESST': [entry for entry in payslip.worked_days_line_ids if entry.code == 'DDESST'],
            'DDESD': [entry for entry in payslip.worked_days_line_ids if entry.code == 'DDESD'],
            'DDESDT': [entry for entry in payslip.worked_days_line_ids if entry.code == 'DDESDT'],
            'FERI': [entry for entry in payslip.worked_days_line_ids if entry.code == 'FERI'],
            'FERIT': [entry for entry in payslip.worked_days_line_ids if entry.code == 'FERIT'],
            'HED': [entry for entry in payslip.worked_days_line_ids if entry.code == 'HED'],
            'HEN': [entry for entry in payslip.worked_days_line_ids if entry.code == 'HEN']
        }
    
        return entry_types
