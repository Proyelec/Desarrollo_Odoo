/** @odoo-module **/
import { CalendarCommonPopover } from "@web/views/calendar/calendar_common/calendar_common_popover";
import { patch } from "@web/core/utils/patch";

patch(CalendarCommonPopover.prototype, {
    /**
     * Override isEventEditable para respetar privacidad de reservaciones.
     * Solo muestra el botón Editar si el usuario puede ver los detalles
     * (es líder, organizador, o asistente de la reunión).
     */
    get isEventEditable() {
        const rawRecord = this.props.record.rawRecord;
        // Si el campo no existe (otro modelo), comportamiento normal
        if (rawRecord.can_see_details === undefined) {
            return true;
        }
        return rawRecord.can_see_details;
    },
});
