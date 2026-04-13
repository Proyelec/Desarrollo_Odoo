# -*- coding: utf-8 -*-
from odoo import api, fields, models


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
        """Retorna True si el usuario actual puede ver los detalles."""
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
        """
        Sobrescribe display_name — usado por el calendario para el título
        de los eventos. Muestra 'Reservada' si el usuario no tiene acceso.
        """
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
            body = (
                f"<p>Hola,</p>"
                f"<p>Has sido invitado a la reservación <b>{self.name}</b>.</p>"
                f"<ul>"
                f"<li><b>Sala:</b> {self.room_id.display_name}</li>"
                f"<li><b>Inicio:</b> {self.start_datetime.strftime('%d/%m/%Y %H:%M')}</li>"
                f"<li><b>Fin:</b> {self.stop_datetime.strftime('%d/%m/%Y %H:%M')}</li>"
            )
            if self.description:
                body += f"<li><b>Agenda:</b> {self.description}</li>"
            body += f"</ul><p>Organizador: <b>{self.organizer_id.name}</b></p>"
        else:
            subject = f"Actualización de reunión: {self.name}"
            body = (
                f"<p>La reservación <b>{self.name}</b> ha sido actualizada.</p>"
                f"<ul>"
                f"<li><b>Sala:</b> {self.room_id.display_name}</li>"
                f"<li><b>Inicio:</b> {self.start_datetime.strftime('%d/%m/%Y %H:%M')}</li>"
                f"<li><b>Fin:</b> {self.stop_datetime.strftime('%d/%m/%Y %H:%M')}</li>"
            )
            if self.description:
                body += f"<li><b>Agenda:</b> {self.description}</li>"
            body += "</ul>"
        partner_ids = self.attendee_ids.mapped("partner_id").ids
        self.message_subscribe(partner_ids=partner_ids)
        self.message_post(
            body=body,
            subject=subject,
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            partner_ids=partner_ids,
        )
