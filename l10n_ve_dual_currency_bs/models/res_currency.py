from odoo import models, fields, api, _
import base64
from odoo.exceptions import UserError
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime

_logger = logging.getLogger(__name__)

class ResCurrency(models.Model):
    _inherit = "res.currency"

    act_productos = fields.Boolean(string='Actualizar Productos')
    server_tax = fields.Selection([('bcv', 'Banco Central De Venezuela')], string='Servidor', default="bcv")
    
    def sud_check_today_rate(self):
        today = datetime.now().date().strftime('%Y-%m-%d')
        rate = self.rate_ids.filtered(lambda r: r.name.strftime('%Y-%m-%d') == today)
        return rate if rate else False

    """
    Este metodo actualiza los precios de los productos de acuerdo a la ultima tasa registrada.
    """
    def action_update_prices(self):
        if not self.rate_ids:
            raise UserError("Debe agregar una Tasa para poder actualizar los precios.")
        rate_day = round(self.rate_ids.sorted('name', reverse=True)[:1].company_rate, 3)
        product_tmp_ids = self.env['product.template'].search([])
        for product_tmp in product_tmp_ids:
            product_tmp.action_update_all_price(rate_day)
        
        mensaje = """
                    <br></br>
                    <span>Los precios de los productos fueron actualizados con la tasa BCV.</span>
        """
        channel = self.env['discuss.channel'].search([('name', '=', 'Tasa de Cambio')])
        if channel:
            channel.message_post(body=mensaje, message_type='comment')

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Acción completada',
                'message': 'La acción ha sido ejecutada exitosamente. Tasa {}'.format(rate_day),
                'sticky': False,
            }
        }

    """
    Toma la tasa oficial de la pagina BCV y la agrega a company_rate en lugar de rate.
    """
    def action_get_tax_BCV(self):
        currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
            
        if currency:
            if not currency.server_tax:
                raise UserError("Seleccione Servidor para el cálculo de la tasa del día.")
    
            if currency.server_tax == 'bcv':
                url = "https://www.bcv.org.ve/tasas-informativas-sistema-bancario"
                response = requests.get(url, verify=False)
                logging.info(response.status_code)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, "html.parser")
                    dolar_element = soup.find("div", {"id": "dolar"})
                    dolar_value = float(dolar_element.text.strip().replace('USD', '').replace('\n', '').replace(' ', '').replace(',', '.'))
                    today_rate = self.sud_check_today_rate()
                    logging.info(f"Tasa obtenida: {dolar_value}")
                    
                    # Establecer la tasa en company_rate en lugar de rate
                    if today_rate:
                        today_rate.company_rate = round(dolar_value, 2)
                    else:
                        # Si no existe una tasa para hoy, crear una nueva entrada con company_rate
                        self.rate_ids = [(0, 0, {
                            'name': datetime.now().date(),
                            'company_rate': round(dolar_value, 2),
                            'currency_id': currency.id
                        })]
                    
                    mensaje = "<h4>Actualización de Tasa BCV : {}</h4>".format(round(dolar_value, 3))
                    
                    channel = self.env['discuss.channel'].search([('name', '=', 'Tasa de Cambio')])
                    if channel:
                        subtye = self.env.ref('mail.mt_comment')
                        channel.message_post(body=mensaje, message_type='comment')
                else:
                    raise UserError(f"Error al realizar la solicitud: {response.status_code}")

    """
    Clase heredada para agregar lógica de advertencia al cambiar company_rate.
    """
    class InheritCurrencyRate(models.Model):
        _inherit = "res.currency.rate"

        @api.onchange('company_rate')
        def _onchange_rate_warning(self):
            latest_rate = self._get_latest_rate()
            if latest_rate:
                diff = (latest_rate.company_rate - self.company_rate) / latest_rate.company_rate
                # Aquí podrías implementar una advertencia si la diferencia es significativa
                # if abs(diff) > 0.2:
                #     return {
                #         'warning': {
                #             'title': _("Warning for %s", self.currency_id.name),
                #             'message': _(
                #                 "The new rate is quite far from the previous rate.\n"
                #                 "Incorrect currency rates may cause critical problems, make sure the rate is correct!"
                #             )
                #         }
                #     }
