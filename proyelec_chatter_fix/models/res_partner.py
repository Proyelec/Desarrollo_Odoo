from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def get_mention_suggestions(self, **kwargs):
        limit = int(kwargs.get("limit") or 8)
        search = kwargs.get("search", "")
        kwargs_super = dict(kwargs)
        kwargs_super["limit"] = limit * 5

        suggestions = super().get_mention_suggestions(**kwargs_super)

        if not isinstance(suggestions, list):
            return suggestions

        partner_ids = [
            s.get("id") for s in suggestions
            if isinstance(s, dict) and s.get("id")
        ]

        allowed_partner_ids = set()
        if partner_ids:
            partners = self.with_context(active_test=False).browse(partner_ids)
            for p in partners:
                internal_users = p.with_context(active_test=False).user_ids.filtered(
                    lambda u: not u.share
                )
                if any(u.active for u in internal_users):
                    allowed_partner_ids.add(p.id)

        result = [
            s for s in suggestions
            if isinstance(s, dict) and s.get("id") in allowed_partner_ids
        ][:limit]

        # Archived partners enter the JS store from message history without the
        # `active` field (mail_message.py calls mail_partner_format with no 'active').
        # partner.active is then undefined in JS, so `=== false` misses them.
        # Returning them here with active=False forces store.Persona.insert() to
        # set active=false, making the JS filter effective on the next render.
        if search:
            archived = self.with_context(active_test=False).search([
                ("active", "=", False),
                "|", ("name", "ilike", search), ("email", "ilike", search),
            ], limit=50)
            archived_internal = archived.filtered(
                lambda p: any(
                    not u.share
                    for u in p.with_context(active_test=False).user_ids
                )
            )
            if archived_internal:
                result.extend(
                    archived_internal.with_context(active_test=False)
                    .mail_partner_format()
                    .values()
                )

        return result
