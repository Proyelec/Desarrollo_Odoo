/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { SuggestionService } from "@mail/core/common/suggestion_service";

patch(SuggestionService.prototype, {
    searchPartnerSuggestions(cleanedSearchTerm, thread, sort) {
        const result = super.searchPartnerSuggestions(...arguments);
        const filterPartners = (partners) =>
            partners.filter((partner) => {
                if (!partner) return false;
                if (partner.active !== true) return false;
                return partner.user && partner.user.isInternalUser === true;
            });
        return {
            ...result,
            mainSuggestions: filterPartners(result.mainSuggestions ?? []),
            extraSuggestions: filterPartners(result.extraSuggestions ?? []),
        };
    },
});
