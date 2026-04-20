/** @odoo-module **/
import { GanttRenderer } from "@web_gantt/gantt_renderer";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(GanttRenderer.prototype, {
    /**
     * Override getDisplayName para usar display_name (que ya devuelve
     * "Reservada" para usuarios sin acceso gracias a _compute_display_name).
     */
    getDisplayName(pill) {
        const record = pill.record;
        if (record.display_name) {
            return record.display_name;
        }
        return super.getDisplayName(pill);
    },

    /**
     * Override getPopoverProps para ocultar el botón Editar
     * en reservaciones privadas donde el usuario no tiene acceso.
     */
    getPopoverProps(pill) {
        const props = super.getPopoverProps(pill);
        const record = pill.record;

        // Si el registro tiene can_see_details y es false, cambiar a "Ver" sin acción
        if (record.can_see_details === false) {
            props.button = {
                text: _t("Reservada"),
                onClick: () => {},  // no hace nada
            };
            // Opcional: eliminar el botón completamente
            props.button = null;
        }

        return props;
    },
});
