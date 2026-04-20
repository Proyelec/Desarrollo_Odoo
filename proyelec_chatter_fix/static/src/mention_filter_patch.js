/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { SuggestionService } from "@mail/core/common/suggestion_service";

patch(SuggestionService.prototype, {
    searchPartnerSuggestions(cleanedSearchTerm, thread, sort) {
        const results = super.searchPartnerSuggestions(...arguments);
        if (!Array.isArray(results)) return results ?? [];
        return results.filter((item) => {
            if (!item) return false;
            const user = item.user;
            if (!user) return false;
            return user.isInternalUser === true;
        });
    },
});
