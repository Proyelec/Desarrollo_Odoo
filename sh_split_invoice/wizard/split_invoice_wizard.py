# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields

class SplitInvoiceWizardLine(models.TransientModel):
    _name = 'sh.split.invoice.wizard.line'
    _description = 'Split Invoice Wizard Line'

    split_line_id = fields.Many2one(
        'sh.split.invoice.wizard', string='Split Invoice Wizard Line')
    qty = fields.Float(string='Quantity')
    product_id = fields.Many2one(
        'product.product', string='Product')


class SplitInvoiceWizard(models.TransientModel):
    _name = 'sh.split.invoice.wizard'
    _description = 'Split Invoice Wizard'

    split_line_ids = fields.One2many(
        'sh.split.invoice.wizard.line', 'split_line_id', string='Split Invoice Wizard')
    company_id = fields.Many2one("res.company",
                                 string="Company",
                                 default=lambda self: self.env.company)

    def action_split(self):
        active_id = self.env.context.get('active_id')
        active_invoice = self.env['account.move'].sudo().with_context(
            check_move_validity=False).browse(active_id)

        ticked_lines = active_invoice.mapped(
            'invoice_line_ids').filtered(lambda x: x.tick)

        if ticked_lines:
            do_unlink = False
            new_invoice_id = False
            for line in active_invoice.invoice_line_ids:
                if line.tick:
                    do_unlink = True
            if do_unlink:
                new_invoice = active_invoice.sudo().with_context(check_move_validity=False).copy()
                new_invoice.split_id = active_invoice.id

                new_invoice_id = new_invoice
                for line in new_invoice_id.invoice_line_ids:
                    if not line.tick:
                        line.sudo().with_context(check_move_validity=False).unlink()
                    else:
                        if self.split_line_ids:
                            for split in self.split_line_ids:
                                if line.tick and split.product_id == line.product_id:
                                    line.sudo().with_context(check_move_validity=False).write(
                                        {'quantity': split.qty})
                                    if self.company_id.sh_invoice_remove_qty:
                                        for lines in active_invoice.invoice_line_ids:
                                            if lines.tick and split.product_id == lines.product_id:
                                                if not split.qty > lines.quantity:
                                                    so_line = lines.quantity - split.qty
                                                    if so_line > 0:
                                                        lines.sudo().with_context(check_move_validity=False).write(
                                                            {'quantity': so_line})
                                                    else:
                                                        lines.sudo().with_context(check_move_validity=False).unlink()
                                                else:
                                                    lines.sudo().with_context(check_move_validity=False).unlink()
                        line.tick = False

        else:
            new_invoice_id = False
            new_invoice = active_invoice.sudo().with_context(check_move_validity=False).copy()
            new_invoice.split_id = active_invoice.id
            new_invoice_id = new_invoice
            for line in new_invoice_id.invoice_line_ids:
                if self.split_line_ids:
                    for split in self.split_line_ids:
                        if split.product_id == line.product_id:
                            line.sudo().with_context(check_move_validity=False).write(
                                {'quantity': split.qty})
                            if self.company_id.sh_invoice_remove_qty:
                                for lines in active_invoice.invoice_line_ids:
                                    if split.product_id == lines.product_id:
                                        if not split.qty > lines.quantity:
                                            so_line = lines.quantity - split.qty
                                            if so_line > 0:
                                                lines.sudo().with_context(check_move_validity=False).write(
                                                    {'quantity': so_line})
                                            else:
                                                lines.sudo().with_context(check_move_validity=False).unlink()
                                        else:
                                            lines.sudo().with_context(check_move_validity=False).unlink()
        if new_invoice_id:
            return{
                'name': 'Invoice/Bill/Credit Note/Debit Note',
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_id': new_invoice_id.id,
                'domain': [('id', '=', new_invoice_id.id)],
                'target': 'current',
            }
