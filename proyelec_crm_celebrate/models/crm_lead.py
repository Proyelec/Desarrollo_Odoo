from odoo import api, fields, models
import logging
from markupsafe import Markup, escape

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def write(self, vals):
        if 'stage_id' in vals:
            new_stage = self.env['crm.stage'].browse(vals['stage_id'])
            if new_stage.is_won:
                leads_to_celebrate = self.filtered(lambda l: not l.stage_id.is_won)
            else:
                leads_to_celebrate = self.env['crm.lead']
        else:
            leads_to_celebrate = self.env['crm.lead']

        result = super().write(vals)

        if leads_to_celebrate:
            leads_to_celebrate._post_celebrate_message()

        return result

    def _post_celebrate_message(self):
        try:
            channel_id = int(
                self.env['ir.config_parameter'].sudo().get_param(
                    'proyelec_crm_celebrate.channel_id', default='0'
                )
            )
            if not channel_id:
                _logger.warning('proyelec_crm_celebrate: channel_id no configurado, omitiendo mensaje')
                return

            channel = self.env['discuss.channel'].sudo().browse(channel_id)
            if not channel.exists():
                _logger.warning('proyelec_crm_celebrate: canal id=%s no existe, omitiendo mensaje', channel_id)
                return

            odoobot = self.env.ref('base.user_root')

            for lead in self:
                fecha = lead.date_deadline or fields.Date.today()
                cliente = lead.partner_id.name if lead.partner_id else '—'

                body = (
                    escape("🏆 ¡OPORTUNIDAD GANADA!")
                    + Markup('<br><br>')
                    + escape(lead.name) + Markup('<br>')
                    + escape(cliente) + Markup('<br>')
                    + escape(str(fecha))
                    + Markup('<br><br>')
                    + escape("¡Felicitaciones al equipo! 💪")
                )

                channel.sudo().with_context(mail_create_nosubscribe=True).message_post(
                    body=body,
                    message_type='comment',
                    subtype_xmlid='mail.mt_comment',
                    author_id=odoobot.partner_id.id,
                )

        except Exception:
            _logger.exception('proyelec_crm_celebrate: error al publicar mensaje de celebración')
