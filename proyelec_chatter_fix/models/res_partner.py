from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def get_mention_suggestions(self, **kwargs):
        limit = int(kwargs.get("limit") or 8)
        kwargs_super = dict(kwargs)
        kwargs_super["limit"] = limit * 5

        suggestions = super().get_mention_suggestions(**kwargs_super)

        if not isinstance(suggestions, list):
            return suggestions

        partner_ids = [
            s.get("id") for s in suggestions
            if isinstance(s, dict) and s.get("id")
        ]
        if not partner_ids:
            return []

        partners = self.with_context(active_test=False).browse(partner_ids)
        allowed_partner_ids = set()
        for p in partners:
            # Buscar usuarios inactivos también con active_test=False
            internal_users = p.with_context(active_test=False).user_ids.filtered(
                lambda u: not u.share
            )
            if any(u.active for u in internal_users):
                allowed_partner_ids.add(p.id)

        return [
            s for s in suggestions
            if isinstance(s, dict) and s.get("id") in allowed_partner_ids
        ][:limit]
