# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools import html2plaintext
from markupsafe import Markup


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
                inicio=self.start_datetime.strftime('%d/%m/%Y %H:%M'),
                fin=self.stop_datetime.strftime('%d/%m/%Y %H:%M'),
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
                inicio=self.start_datetime.strftime('%d/%m/%Y %H:%M'),
                fin=self.stop_datetime.strftime('%d/%m/%Y %H:%M'),
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
