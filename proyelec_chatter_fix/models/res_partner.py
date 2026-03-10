from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def get_mention_suggestions(self, **kwargs):
        """
        Odoo 17 @mention autocomplete calls:
            model: res.partner
            method: get_mention_suggestions
            kwargs: {search: "...", context: {...}, (optional) limit: N}

        Goal:
        - Exclude ex-employees (internal users with active=False) from dropdown
        - Do NOT affect mail.message history
        - Do NOT touch name_search (avoid side effects in accounting/sales/etc.)
        """

        # Defensive defaults: Odoo may omit limit.
        limit = int(kwargs.get("limit") or 8)

        # Ask for more results, then filter, so we still return up to `limit`
        raw_limit = max(limit * 3, 20)
        kwargs_super = dict(kwargs)
        kwargs_super["limit"] = raw_limit

        suggestions = super().get_mention_suggestions(**kwargs_super)

        # Fail-safe: if format changes, return original behavior (trimmed)
        if not isinstance(suggestions, list):
            return suggestions

        partner_ids = [
            s.get("id") for s in suggestions
            if isinstance(s, dict) and s.get("id")
        ]
        if not partner_ids:
            return suggestions[:limit]

        # active_test=False to be safe with archived partners/users relations
        partners = self.browse(partner_ids).with_context(active_test=False)

        allowed_partner_ids = set()
        for p in partners:
            # Only internal users matter (share=False). Portal users are ignored here.
            internal_users = p.user_ids.filtered(lambda u: not u.share)

            # No internal user linked => external contact/customer/supplier => keep
            if not internal_users:
                allowed_partner_ids.add(p.id)
                continue

            # Keep if at least one internal user is active
            if any(u.active for u in internal_users):
                allowed_partner_ids.add(p.id)
            # else: all internal users inactive => exclude from dropdown

        filtered = [
            s for s in suggestions
            if isinstance(s, dict) and s.get("id") in allowed_partner_ids
        ]
        return filtered[:limit]
