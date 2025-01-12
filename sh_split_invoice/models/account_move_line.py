# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    tick = fields.Boolean(string="Select Product")

    def btn_tick_untick(self):
        if self.tick:
            self.sudo().with_context(check_move_validity=False).tick = False
        else:
            self.sudo().with_context(check_move_validity=False).tick = True
