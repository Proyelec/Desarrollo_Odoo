# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields

class AccountMove(models.Model):
    _inherit = "account.move"

    extract_id = fields.Many2one(
        'account.move', 'Extracted From', tracking=True, readonly=True, copy=False)
    split_id = fields.Many2one('account.move', 'Splited From',
                               tracking=True, readonly=True, copy=False)
    extract_count = fields.Integer(
        'Extracted', compute='_compute_extract_count')
    split_count = fields.Integer(
        'Splited', compute='_compute_split_count')

    def _compute_extract_count(self):
        if self:
            for rec in self:
                rec.extract_count = 0
                extract_ids = self.env['account.move'].sudo().with_context(check_move_validity=False).search(
                    [('extract_id', '=', rec.id)])
                if extract_ids:
                    rec.extract_count = len(extract_ids.ids)

    def _compute_split_count(self):
        if self:
            for rec in self:
                rec.split_count = 0
                split_ids = self.env['account.move'].sudo().with_context(check_move_validity=False).search(
                    [('split_id', '=', rec.id)])
                if split_ids:
                    rec.split_count = len(split_ids.ids)

    def action_view_extract_invoice(self):
        self.ensure_one()
        return{
            'name': 'Extracted Invoices/Bills/Credit Notes/Debit Notes',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'domain': [('extract_id', '=', self.id)],
            'target': 'current'
        }

    def action_view_split_invoice(self):
        self.ensure_one()
        return{
            'name': 'Splited Invoices/Bills/Credit Notes/Debit Notes',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'domain': [('split_id', '=', self.id)],
            'target': 'current'
        }

    def action_split(self):
        context = {}
        line_list = []
        ticked_lines = False
        unticked_lines = False

        if self.invoice_line_ids:
            ticked_lines = self.mapped(
                'invoice_line_ids').filtered(lambda x: x.tick)
            unticked_lines = self.mapped(
                'invoice_line_ids').filtered(lambda x: not x.tick)

            if ticked_lines:
                for line in ticked_lines:
                    line_vals = {
                        'product_id': line.product_id.id,
                        'qty': line.quantity,
                    }
                    line_list.append((0, 0, line_vals))
            else:
                if unticked_lines:
                    for line in unticked_lines:
                        line_vals = {
                            'product_id': line.product_id.id,
                            'qty': line.quantity,
                        }
                        line_list.append((0, 0, line_vals))

            context.update({
                'default_split_line_ids': line_list
            })
        return{
            'name': 'Split Invoice/Bill/Credit Note/Debit Note',
            'res_model': 'sh.split.invoice.wizard',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'context': context,
            'target': 'new'
        }

    def action_extract(self):
        do_unlink = False
        new_move_id = False
        for rec in self:
            for line in rec.invoice_line_ids:
                if line.tick:
                    do_unlink = True
            if do_unlink:
                new_move = rec.sudo().with_context(check_move_validity=False).copy()
                new_move.extract_id = rec.id
                new_move_id = new_move
                for line in new_move.invoice_line_ids:
                    if not line.tick:
                        line.sudo().with_context(check_move_validity=False).unlink()
                    else:
                        line.tick = False
            for line in rec.invoice_line_ids:
                if line.tick:
                    line.tick = False
        if new_move_id:
            return{
                'name': 'Invoice/Bill/Credit Note/Debit Note',
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_id': new_move_id.id,
                'domain': [('id', '=', new_move_id.id)],
                'target': 'current',
            }

    def action_check(self):
        if self.invoice_line_ids:
            for line in self.invoice_line_ids:
                line.sudo().with_context(check_move_validity=False).write({
                    'tick': True
                })

    def action_uncheck(self):
        if self.invoice_line_ids:
            for line in self.invoice_line_ids:
                line.sudo().with_context(check_move_validity=False).write({
                    'tick': False
                })
