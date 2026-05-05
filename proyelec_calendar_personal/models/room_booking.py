# -*- coding: utf-8 -*-
from odoo import api, fields, models


class RoomBooking(models.Model):
    _inherit = 'room.booking'

    calendar_event_id = fields.Many2one(
        'calendar.event',
        string='Evento de calendario',
        copy=False,
        ondelete='set null',
    )

    @api.model_create_multi
    def create(self, vals_list):
        bookings = super().create(vals_list)
        for booking in bookings:
            booking._sync_to_calendar()
        return bookings

    def write(self, vals):
        res = super().write(vals)
        if {'start_datetime', 'stop_datetime', 'room_id', 'name', 'attendee_ids'} & vals.keys():
            for booking in self:
                booking._sync_to_calendar()
        return res

    def unlink(self):
        for booking in self:
            if booking.calendar_event_id:
                booking.calendar_event_id.sudo().unlink()
        return super().unlink()

    def _sync_to_calendar(self):
        self.ensure_one()
        partner_ids = self.attendee_ids.mapped('partner_id').ids
        if self.organizer_id.partner_id:
            partner_ids = list(set(partner_ids + [self.organizer_id.partner_id.id]))
        vals = {
            'name': self.name,
            'start': self.start_datetime,
            'stop': self.stop_datetime,
            'partner_ids': [(6, 0, partner_ids)],
            'location': self.room_id.display_name,
            'description': self.description or '',
            'privacy': 'confidential' if self.is_private else 'public',
            'show_as': 'busy',
        }
        if self.calendar_event_id:
            self.calendar_event_id.sudo().write(vals)
        else:
            event = self.env['calendar.event'].sudo().create(vals)
            self.sudo().write({'calendar_event_id': event.id})