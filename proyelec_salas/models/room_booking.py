# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools import html2plaintext
from markupsafe import Markup
import pytz
from datetime import timedelta


class RoomBooking(models.Model):
    _inherit = "room.booking"

    description = fields.Text(string="Agenda / Descripción")
    attendee_ids = fields.Many2many(
        "res.users",
        "room_booking_attendee_rel",
        "booking_id",
        "user_id",
        string="Asistentes",
    )
    is_private = fields.Boolean(string="Privada", default=True, tracking=6)
    can_see_details = fields.Boolean(
        compute="_compute_can_see_details",
    )
    reminder_15_sent = fields.Boolean(
        string="Recordatorio 15 min enviado",
        default=False,
        copy=False,
    )
    reminder_5_sent = fields.Boolean(
        string="Recordatorio 5 min enviado",
        default=False,
        copy=False,
    )

    def _user_can_see(self):
        self.ensure_one()
        if not self.id:
            return True
        is_leader = self.env.user.has_group(
            "proyelec_salas.group_room_booking_leader"
        )
        return (
            is_leader
            or not self.is_private
            or self.organizer_id == self.env.user
            or self.env.user in self.attendee_ids
        )

    def _compute_can_see_details(self):
        is_leader = self.env.user.has_group(
            "proyelec_salas.group_room_booking_leader"
        )
        for booking in self:
            if not booking.id:
                booking.can_see_details = True
                continue
            booking.can_see_details = (
                is_leader
                or not booking.is_private
                or booking.organizer_id == self.env.user
                or self.env.user in booking.attendee_ids
            )

    def _compute_display_name(self):
        is_leader = self.env.user.has_group(
            "proyelec_salas.group_room_booking_leader"
        )
        for booking in self:
            if not booking.id:
                booking.display_name = booking.name or ""
                continue
            can_see = (
                is_leader
                or not booking.is_private
                or booking.organizer_id == self.env.user
                or self.env.user in booking.attendee_ids
            )
            booking.display_name = booking.name if can_see else "Reservada"

    @api.model_create_multi
    def create(self, vals_list):
        bookings = super().create(vals_list)
        for booking in bookings:
            booking._notify_attendees("create")
        return bookings

    def write(self, vals):
        res = super().write(vals)
        if {"attendee_ids", "start_datetime", "stop_datetime", "room_id"} & vals.keys():
            for booking in self:
                booking._notify_attendees("update")
        return res

    def _format_datetime_tz(self, dt):
        """Convierte datetime UTC a la zona horaria del organizador."""
        tz_name = (
            self.organizer_id.tz
            or self.env.user.tz
            or 'America/Caracas'
        )
        user_tz = pytz.timezone(tz_name)
        dt_local = pytz.utc.localize(dt).astimezone(user_tz)
        return dt_local.strftime('%d/%m/%Y %H:%M')

    def _notify_attendees(self, action="create"):
        self.ensure_one()
        if not self.attendee_ids:
            return
        if action == "create":
            subject = f"Invitación a reunión: {self.name}"
            body = Markup(
                "<p>Hola,</p>"
                "<p>Has sido invitado a la reservación <b>{name}</b>.</p>"
                "<ul>"
                "<li><b>Sala:</b> {sala}</li>"
                "<li><b>Inicio:</b> {inicio}</li>"
                "<li><b>Fin:</b> {fin}</li>"
                "{agenda}"
                "</ul>"
                "<p>Organizador: <b>{organizador}</b></p>"
            ).format(
                name=self.name,
                sala=self.room_id.display_name,
                inicio=self._format_datetime_tz(self.start_datetime),
                fin=self._format_datetime_tz(self.stop_datetime),
                agenda=Markup("<li><b>Agenda:</b> {}</li>").format(self.description) if self.description else Markup(""),
                organizador=self.organizer_id.name,
            )
        else:
            subject = f"Actualización de reunión: {self.name}"
            body = Markup(
                "<p>La reservación <b>{name}</b> ha sido actualizada.</p>"
                "<ul>"
                "<li><b>Sala:</b> {sala}</li>"
                "<li><b>Inicio:</b> {inicio}</li>"
                "<li><b>Fin:</b> {fin}</li>"
                "{agenda}"
                "</ul>"
            ).format(
                name=self.name,
                sala=self.room_id.display_name,
                inicio=self._format_datetime_tz(self.start_datetime),
                fin=self._format_datetime_tz(self.stop_datetime),
                agenda=Markup("<li><b>Agenda:</b> {}</li>").format(self.description) if self.description else Markup(""),
            )
        partner_ids = self.attendee_ids.mapped("partner_id").ids
        self.message_subscribe(partner_ids=partner_ids)
        self.message_post(
            body=body,
            subject=subject,
            message_type="email",
            subtype_xmlid="mail.mt_comment",
            partner_ids=partner_ids,
        )

    @api.model
    def _send_meeting_reminders(self):
        """Cron: envía recordatorios 15 y 5 minutos antes de cada reunión."""
        now = fields.Datetime.now()
        window_15_start = now + timedelta(minutes=14)
        window_15_end = now + timedelta(minutes=16)
        window_5_start = now + timedelta(minutes=4)
        window_5_end = now + timedelta(minutes=6)

        # Recordatorio 15 minutos
        bookings_15 = self.search([
            ('start_datetime', '>=', window_15_start),
            ('start_datetime', '<=', window_15_end),
            ('reminder_15_sent', '=', False),
        ])
        for booking in bookings_15:
            partner_ids = booking.attendee_ids.mapped("partner_id").ids
            if booking.organizer_id.partner_id:
                partner_ids = list(set(partner_ids + [booking.organizer_id.partner_id.id]))
            if not partner_ids:
                continue
            body = Markup(
                "⏰ <b>La reunión comenzará en 15 minutos.</b><br/>"
                "📍 <b>Sala:</b> {sala}"
            ).format(sala=booking.room_id.display_name)
            booking.message_post(
                body=body,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
                partner_ids=partner_ids,
            )
            booking.sudo().write({'reminder_15_sent': True})

        # Recordatorio 5 minutos
        bookings_5 = self.search([
            ('start_datetime', '>=', window_5_start),
            ('start_datetime', '<=', window_5_end),
            ('reminder_5_sent', '=', False),
        ])
        for booking in bookings_5:
            partner_ids = booking.attendee_ids.mapped("partner_id").ids
            if booking.organizer_id.partner_id:
                partner_ids = list(set(partner_ids + [booking.organizer_id.partner_id.id]))
            if not partner_ids:
                continue
            body = Markup(
                "🔔 <b>La reunión comenzará en 5 minutos.</b><br/>"
                "📍 <b>Sala:</b> {sala}"
            ).format(sala=booking.room_id.display_name)
            booking.message_post(
                body=body,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
                partner_ids=partner_ids,
            )
            booking.sudo().write({'reminder_5_sent': True})