##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from re import search
from datetime import datetime, timedelta
from odoo import models, fields, api, _
import json
# import time
import logging
import xlsxwriter
import shutil
import base64
import csv
import xlwt

_logger = logging.getLogger(__name__)

class AccountVatLedgerXlsx(models.AbstractModel):
    _name = 'report.l10n_ve_vat_ledger.account_vat_ledger_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Xlsx Account VAT Ledger"

    """
        Este metodo permite tomar el total de facturas por dia , esto es para que luego que se finalice de pintar
        todas las facturas POR DÍAS en el Excel pinta Las retenciones del mismo dia.
    """
    def getTotalInvoiceDate(self,invoices):
        lista_fechas = [inv.invoice_date.strftime('%d/%m/%Y') for inv in invoices]
        total_facturas = {}
        # Recorrer la lista de fechas para contar el número de facturas por fecha
        for fecha in lista_fechas:
            if fecha in total_facturas:
                total_facturas[fecha] += 1  # Si la fecha ya está en el diccionario, incrementar el contador
            else:
                total_facturas[fecha] = 1  # Si la fecha no está en el diccionario, agregarla con un contador de 1
        
        return total_facturas

    def find_values(self, id, json_repr):
        results = []

        def _decode_dict(a_dict):
            try:
                results.append(a_dict[id])
            except KeyError:
                pass
            return a_dict
        # Return value ignored.
        json.loads(json_repr, object_hook=_decode_dict)
        return results


    def generate_xlsx_report(self, workbook, data, account_vat):
        for obj in account_vat:
            report_name = obj.name
            sheet = workbook.add_worksheet(report_name[:31])
            title = workbook.add_format({'bold': True})
            bold = workbook.add_format({'bold': True, 'border':1})


            # Resumen IVA
            # sheet2 = workbook.add_worksheet('Resumen consolidado de IVA')

            # style nuevo
            cell_format = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'fg_color': '#a64d79',
                'font_color': 'white',
                'text_wrap': 1,
                'num_format': '0',})
            
            cell_format_3 = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': 1,
                'num_format': '0',})

            cell_format_1 = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'fg_color': '#a64d79',
                'font_color': 'white'})

            cell_format_2 = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'left',
                'fg_color': '#a64d79',
                'font_color': 'white'})

            title = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'})

            title_style = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'left'})

            line = workbook.add_format({
                'border': 1,
                'align': 'center',
                'num_format': '#,##0.00'
                })

            line_total = workbook.add_format({
                'border': 1,
                'fg_color': '#f0f0f0',
                'bold': 1,
                'align': 'center',
                'num_format': '#,##0.00'})

            date_line = workbook.add_format(
                {'border': 1, 'num_format': 'dd-mm-yyyy',
                 'align': 'center'})

            sheet.set_column(0, 0, 9)
            sheet.set_column(1, 4, 20)
            sheet.set_column(5, 10, 13)
            sheet.set_column(11, 14, 24)

            # Establece el ancho de la columna A en 30
            sheet.set_column(5, 5, 30)
            sheet.set_column(5, 6, 30)
            sheet.set_column(5, 7, 30)
            sheet.set_column(5, 8, 30)
            sheet.set_column(5, 9, 30)
            sheet.set_column(5, 11, 30)
            sheet.set_column(5, 12, 30)
            sheet.set_column(5, 13, 30)
            sheet.set_column(5, 14, 30)
            sheet.set_column(5, 15, 30)
            sheet.set_column(5, 16, 30)
            sheet.set_column(5, 17, 30)
            sheet.set_column(5, 18, 30)
            sheet.set_column(5, 19, 30)
            sheet.set_column(5, 20, 30)
            sheet.set_column(5, 21, 30)
            sheet.set_column(5, 22, 30)
            sheet.set_column(5, 23, 30)
            sheet.set_column(5, 24, 30)
            sheet.set_column(5, 25, 30)
            sheet.set_column(5, 26, 30)
            sheet.set_column(5, 27, 30)
            sheet.set_column(5, 28, 30)
            sheet.set_column(5, 29, 30)
            sheet.set_column(5, 30, 30)
# _____________________________________________________________________________________
# _____________________________________________________________________________________
            if obj.type == 'purchase':

                sheet.merge_range('A1:D1', obj.company_id.name,title_style)
                sheet.merge_range('A2:D2', obj.company_id.street,title_style)
                sheet.merge_range('A3:D3', _('%s-%s', obj.company_id.l10n_latam_identification_type_id.l10n_ve_code, obj.company_id.vat), title_style)
                sheet.merge_range('A4:G4', obj.name + ' ' + 'Libro de IVA Compras' + ' ', title_style)

                # alto de las celdas
                sheet.set_row(4, 30)

                sheet.write(4, 0, 'Nro Oper.', cell_format)
                sheet.write(4, 1, 'Fecha de la Factura o Documento', cell_format)
                sheet.write(4, 2, 'Tipo de Documento', cell_format)
                sheet.write(4, 3, 'Número de Documento', cell_format)
                sheet.write(4, 4, 'Número de Control', cell_format)
                sheet.write(4, 5, 'Número de Comprobante', cell_format)
                sheet.write(4, 6, 'Número Factura Afectada', cell_format)
                sheet.write(4, 7, 'Nª planilla de Importaciòn', cell_format)
                sheet.write(4, 8, 'Nª de Expediente de Importaciòn', cell_format)
                sheet.write(4, 9, 'Nombre o Razón Social', cell_format)
                sheet.write(4, 10, 'RIF', cell_format)
                sheet.write(4, 11, 'Total Compras  Bs. Incluyendo IVA.', cell_format)
                sheet.write(4, 12, 'Compras sin Derecho a Crédito I.V.A.', cell_format)

                # celda adicional compras por cuenta de terceros
                sheet.merge_range('N4:P4','Importaciones', cell_format)
                sheet.write(4, 13, 'Base Imponible', cell_format)
                sheet.write(4, 14, '% Alic.', cell_format)
                sheet.write(4, 15, 'Imp. I.V.A.', cell_format)

                # # IVA RETENIDO
                sheet.merge_range('Q4:W4', 'Compras Internas', cell_format)
                sheet.write(4, 16, 'Base Imponible', cell_format)
                sheet.write(4, 17, 'Alicuota 16%', cell_format)
                sheet.write(4, 18, 'Imp. I.V.A.', cell_format)
                sheet.write(4, 19, 'B. Imponible', cell_format)
                sheet.write(4, 20, 'Alicuota 8%', cell_format)
                sheet.write(4, 21, 'Imp. I.V.A.', cell_format)

                # sheet.write(4, 22, 'B. Imponible', cell_format)
                # sheet.write(4, 23, 'Alicuota 31%', cell_format)
                # sheet.write(4, 24, 'Imp. I.V.A.', cell_format)

                sheet.write(4, 22, 'I.V.A. Retenido por el comprador', cell_format)
                # sheet.write(4, 26, 'I.G.T.F Pagado  ', cell_format)

            elif obj.type == 'sale':

                sheet.merge_range('A1:D1', obj.company_id.name, title_style)
                sheet.merge_range('A2:D2', obj.company_id.street, title_style)
                # sheet.merge_range('E2:S2', 'LIBRO DE VENTAS (FECHA DESDE:' + ' ' + str(obj.date_from) + ' ' + 'HASTA:' + ' ' + str(obj.date_from) + ')', title)
                sheet.merge_range('A3:D3', _('%s-%s', obj.company_id.l10n_latam_identification_type_id.l10n_ve_code, obj.company_id.vat), title_style)
                sheet.merge_range('A4:G4', obj.name + ' ' + 'Libro de IVA Ventas' + ' ' + 'mes' + ' ' + 'Año',
                                  title_style)

                # alto de las celdas
                sheet.set_row(4, 31)

                sheet.write(4, 0, 'Nro Oper.', cell_format_3)
                sheet.write(4, 1, 'Fecha de la Factura', cell_format)
                sheet.write(4, 2, 'Tipo de Documento', cell_format)
                sheet.write(4, 3, 'Factura o Número de Documento', cell_format)
                # Celda adicional de ticket fiscal
                #sheet.write(4, 30, 'Ticket Fiscal', cell_format)
                sheet.write(4, 4, 'Número de Control', cell_format)
                sheet.write(4, 5, 'N° comprobante', cell_format)
                sheet.write(4, 6, 'Número Factura Afectada', cell_format)
                sheet.write(4, 7, 'Nombre o Razón Social', cell_format)
                sheet.write(4, 8, 'RIF', cell_format)
                sheet.write(4, 9, 'Total Ventas  Bs. Incluyendo IVA.', cell_format)

                # celda adicional Ventas por cuenta de terceros
                sheet.merge_range('K4:N4', 'Ventas por cuenta de terceros', cell_format)
                sheet.write(4, 10, 'Ventas Internas No Gravadas', cell_format)
                sheet.write(4, 11, 'Base Imponible', cell_format)
                sheet.write(4, 12, '% Alicuota.', cell_format)
                sheet.write(4, 13, 'Impuesto I.V.A', cell_format)

                # celda adicional Contribuyente
                sheet.merge_range('O4:U4', 'Contribuyente', cell_format)
                sheet.write(4, 14, 'Ventas Internas No Gravadas', cell_format)
                sheet.write(4, 15, 'Base Imponible', cell_format)
                sheet.write(4, 16, '% Alicuota General + Adicional', cell_format)
                sheet.write(4, 17, 'Impuesto I.V.A', cell_format)
                sheet.write(4, 18, 'Base Imponible', cell_format)
                sheet.write(4, 19, '% Alicuota Reducida', cell_format)
                sheet.write(4, 20, 'Impuesto I.V.A', cell_format)

                # celda adicional No Contribuyente
                sheet.merge_range('V4:AB4', 'No Contribuyente', cell_format)
                sheet.write(4, 21, 'Ventas Internas No Gravadas', cell_format)
                sheet.write(4, 22, 'Base Imponible', cell_format)
                sheet.write(4, 23, '% Alicuota.', cell_format)
                sheet.write(4, 24, 'Impuesto I.V.A', cell_format)
                sheet.write(4, 25, 'Base Imponible', cell_format)
                sheet.write(4, 26, '% Alicuota Reducida', cell_format)
                sheet.write(4, 27, 'Impuesto I.V.A', cell_format)

                # celda adicional Retención IVA
                # sheet.merge_range('AB4:AD4', 'Retención IVA', cell_format)
                sheet.write(4, 28, 'I.V.A Retenido', cell_format)
                # sheet.write(4, 29, 'Factura afectada', cell_format)
                sheet.write(4, 29, 'I.G.T.F Percibido', cell_format)

                

            row = 5
            total_base_exento = 0.00
            total_base_exento_credito = 0.00
            total_base_exento_debito = 0.00
            total_base_imponible_16 = 0.00
            total_iva_16 = 0.00
            total_iva_16_retenido = 0.00
            total_iva_16_igtf = 0.00

            total_base_imponible_8 = 0.00
            total_iva_8 = 0.00
            total_iva_8_igtf = 0.00

            total_base_imponible_15 = 0.00
            total_iva_15 = 0.00
            total_iva_15_igtf = 0.00
            alic = ''

            # total_base_imponible_31 = 0.00
            # total_iva_31 = 0.00

            total_nota_credito_16 = 0.00
            total_nota_credito_iva_16 = 0.00
            total_nota_credito_8 = 0.00
            total_nota_credito_iva_8 = 0.00
            # total_nota_credito_31 = 0.00
            # total_nota_credito_iva_31 = 0.00
            total_nota_debito_16 = 0.00
            total_nota_debito_iva_16 = 0.00
            total_nota_debito_8 = 0.00
            total_nota_debito_iva_8 = 0.00
            # total_nota_debito_31 = 0.00
            # total_nota_debito_iva_31 = 0.00

            """ 
                Totales columnas ventas
             """

            total_base_exento_contribuyente = 0.00
            total_base_imponible_contribuyente_16 = 0.00
            total_iva_contribuyente_16 = 0.00
            total_base_imponible_contribuyente_8 = 0.00
            total_iva_contribuyente_8 = 0.00

            total_base_exento_no_contribuyente = 0.00
            total_base_imponible_no_contribuyente_16 = 0.00
            total_iva_no_contribuyente_16 = 0.00
            total_base_imponible_no_contribuyente_8 = 0.00
            total_iva_no_contribuyente_8 = 0.00

            """ 
                Totales columnas compras
             """

            c_total_base_exento = 0.00
            c_total_base_imponible_16 = 0.00
            c_total_iva_16 = 0.00
            c_total_base_imponible_8 = 0.00
            c_total_iva_8 = 0.00
            # c_total_base_imponible_31 = 0.00
            # c_total_iva_31 = 0.00
            c_total_igtf = 0.00
          
            i = 0
            
            """
            Retenciones
            """

            retenciones = []

            tax_withholding_id = []
            if obj.type == 'purchase':
                tax_withholding_id = self.env['account.tax'].search([
                    ('type_tax_use', '=', 'supplier'),
                    ('withholding_type', '=', 'partner_tax'),
                    ('company_id', '=', obj.company_id.id),
                ], limit=1)
            else:
                tax_withholding_id = self.env['account.tax'].search([
                    ('type_tax_use', '=', 'customer'),
                    ('name', 'like', 'IVA'),
                    ('company_id', '=', obj.company_id.id),
                ], limit=1)

            logging.info(tax_withholding_id)

            invoices = sorted(obj.invoice_ids, key=lambda x: x.invoice_date)

            date_reference = obj.date_from

            totalsFoDayInv = self.getTotalInvoiceDate(invoices)
            fi = 1
            listinv = []
            logging.info("FACTURAS-------------------")
            logging.info(invoices)

            for idx, invoice in enumerate(invoices):
                dinv = invoice.invoice_date.strftime('%d/%m/%Y')
                if obj.type == 'purchase':
                    if fi == totalsFoDayInv[dinv] and dinv not in listinv:
                        logging.info(f"Vamos por {dinv}  total numero de facturas {totalsFoDayInv[dinv]}")
                        listinv.append(dinv)
                        fi = 1

                        # Verificar si la factura tiene retención de IVA
                        if invoice.withholding_iva and invoice.withholding_number:
                            total_iva_16_retenido += invoice.withholding_iva
                            i += 1
                            # Código
                            sheet.write(row, 0, i, cell_format_3)
                            # Fecha
                            sheet.write(row, 1, invoice.invoice_date, date_line)
                            # Tipo de documento
                            sheet.write(row, 2, 'Retención', line)
                            sheet.write(row, 3, '', line)
                            sheet.write(row, 4, '', line)
                            # Número de comprobante
                            sheet.write(row, 5, invoice.withholding_number, line)
                            # Documento afectado
                            sheet.write(row, 6, invoice.ref or invoice.reference_number, line)
                            sheet.write(row, 7, '', line)
                            sheet.write(row, 8, '', line)
                            # Nombre
                            sheet.write(row, 9, invoice.partner_id.name, line)
                            # RIF
                            sheet.write(row, 10, '%s-%s' % (invoice.partner_id.l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                                                            invoice.partner_id.vat or 'FALSE'), line)
                            # Total
                            sheet.write(row, 11, '', line)
                            # Compras Exento
                            sheet.write(row, 12, '', line)

                            # IMPORTACIONES
                            # Base Imponible
                            sheet.write(row, 13, '', line)
                            # % Alic
                            sheet.write(row, 14, '', line)
                            # Imp. IVA
                            sheet.write(row, 15, '', line)

                            # Compras internas
                            # Base Imponible
                            sheet.write(row, 16, '', line)
                            # % Alic
                            sheet.write(row, 17, '', line)
                            # Imp. IVA
                            sheet.write(row, 18, '', line)

                            # IVA 8%
                            # Base Imponible
                            sheet.write(row, 19, '', line)
                            # % Alic
                            sheet.write(row, 20, '', line)
                            # Imp. IVA
                            sheet.write(row, 21, '', line)

                            # # IVA 31%
                            # # Base Imponible
                            # sheet.write(row, 22, '', line)
                            # # % Alic
                            # sheet.write(row, 23, '', line)
                            # # Imp. IVA
                            # sheet.write(row, 24, '', line)

                            # Retenciones
                            sheet.write(row, 22, abs(invoice.withholding_iva), line)
                            ###### IGTF
                            # sheet.write(row, 26, '', line)
                            row += 1
                    else:
                        fi += 1

                    i += 1
                    # Contador de la factura
                    sheet.write(row, 0, i, cell_format_3)
                    # Fecha
                    sheet.write(row, 1, invoice.invoice_date or 'FALSE', date_line)
                    # Tipo de documento
                    if invoice.move_type == 'out_invoice':
                        sheet.write(row, 2, 'Factura', line)
                    elif invoice.move_type == 'out_refund' and not invoice.debit_origin_id:
                        sheet.write(row, 2, 'Nota de Credito', line)
                    elif invoice.move_type == 'out_refund' and invoice.debit_origin_id:
                        sheet.write(row, 2, 'Nota de Debito', line)
                    elif invoice.move_type == 'in_invoice':
                        sheet.write(row, 2, 'Factura', line)
                    elif invoice.move_type == 'in_refund' and not invoice.debit_origin_id:
                        sheet.write(row, 2, 'Nota de Credito', line)
                    elif invoice.move_type == 'in_refund' and invoice.debit_origin_id:
                        sheet.write(row, 2, 'Nota de Debito', line)
                    # Número de Documento
                    sheet.write(row, 3, invoice.ref or invoice.reference_number or '', line)
                    # Número de Control
                    sheet.write(row, 4, invoice.l10n_ve_document_number or '', line)
                    # Ticket Fiscal
                    sheet.write(row, 5, '', line)

                    # Número Factura Afectada si es de débito o crédito
                    if invoice.move_type == 'in_refund' or invoice.move_type == 'out_refund':
                        move_reconcileds = invoice._get_reconciled_info_JSON_values()
                        inv_info = ''
                        moves = []
                        if move_reconcileds:
                            for m in move_reconcileds:
                                moves.append(m['move_id'])
                            move_ids = self.env['account.move'].search([('id', 'in', moves)])
                            for mov in move_ids:
                                if mov.move_type == 'in_invoice' and mov.state == 'posted':
                                    inv_info = mov.ref
                            sheet.write(row, 6, inv_info, line)
                    else:
                        sheet.write(row, 6, '', line)

                    # Planilla de importación
                    sheet.write(row, 7, '', line)
                    # Nro Expediente de importación
                    sheet.write(row, 8, '', line)
                    # Nombre del partner
                    sheet.write(row, 9, invoice.partner_id.name or 'FALSE', line)

                    # Rif del cliente
                    sheet.write(row, 10, '%s-%s' % (invoice.partner_id.l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                                                    invoice.partner_id.vat or 'FALSE'), line)

                    # Total Compras con IVA
                    sheet.write(row, 11, (abs(invoice.amount_total_bs)), line)

                    # Inicialización de valores
                    base_exento = 0.00
                    base_imponible_16 = 0.00
                    base_imponible_8 = 0.00
                    # base_imponible_31 = 0.00
                    iva_16 = 0.00
                    iva_8 = 0.00
                    # iva_31 = 0.00
                    igtf_amount = 0.00

                    alic_16 = ''
                    alic_8 = ''
                    # alic_31 = ''

                    # Tasa de cambio y factor
                    tasa_cambio = invoice.tax_day if invoice.currency_id.name == 'USD' else 1
                    factor = -1 if invoice.move_type in ['out_refund', 'in_refund'] else 1

                    # Recorrer líneas de la factura para calcular bases imponibles
                    for inv_line in invoice.invoice_line_ids:
                        line_base = inv_line.price_subtotal * tasa_cambio * factor

                        if not inv_line.tax_ids:
                            # Si la línea no tiene impuestos, es exenta
                            base_exento += line_base
                            continue

                        for tax in inv_line.tax_ids:
                            if tax.amount == 16.0:
                                base_imponible_16 += line_base
                                alic_16 = '16%'
                            elif tax.amount == 8.0:
                                base_imponible_8 += line_base
                                alic_8 = '8%'
                            # elif tax.amount == 31.0:
                            #     base_imponible_31 += line_base
                            #     alic_31 = '31%'

                    # Recorrer líneas contables para calcular el IVA
                    for move_line in invoice.line_ids:
                        if move_line.tax_line_id:
                            tax = move_line.tax_line_id
                            # tax_amount = move_line.balance * tasa_cambio * factor

                            if tax.amount == 16.0:
                                iva_16 += base_imponible_16 * 0.16
                            elif tax.amount == 8.0:
                                iva_8 += base_imponible_8 * 0.08
                            # elif tax.amount == 31.0:
                            #     iva_31 += base_imponible_31 * 0.31

                    # Si hay IGTF, aplicarlo
                    igtf_amount = (invoice.igtf_amount_purchase if invoice.igtf_purchase_apply_purchase else 0.00) * factor

                    # Cálculo de bases imponibles por impuesto (si tienes certeza de que funciona bien)
                    baseImponibleTax = invoice.calcular_base_imponible_por_impuesto_USD()
                    baseImp_16 = baseImponibleTax.get("IVA (16.0%) compras", 0.00) * tasa_cambio
                    baseImp_8 = baseImponibleTax.get("IVA (8.0%) compras", 0.00) * tasa_cambio

                    # Actualización de acumuladores totales
                    c_total_base_exento += base_exento
                    c_total_base_imponible_16 += base_imponible_16
                    c_total_iva_16 += iva_16
                    c_total_base_imponible_8 += base_imponible_8
                    c_total_iva_8 += iva_8
                    # c_total_base_imponible_31 += base_imponible_31
                    # c_total_iva_31 += iva_31
                    c_total_igtf += igtf_amount

                    # Escribir en la hoja Excel
                    sheet.write(row, 12, round(base_exento, 2), line)  # Compras Exento

                    # IMPORTACIONES
                    sheet.write(row, 13, '', line)  # Base Imponible
                    sheet.write(row, 14, '', line)  # % Alic
                    sheet.write(row, 15, '', line)  # Imp. IVA

                    # Compras internas 16%
                    sheet.write(row, 16, round(baseImp_16, 2), line)
                    sheet.write(row, 17, alic_16, line)
                    sheet.write(row, 18, round(iva_16, 2), line)

                    # Compras internas 8%
                    sheet.write(row, 19, round(baseImp_8, 2), line)
                    sheet.write(row, 20, alic_8, line)
                    sheet.write(row, 21, round(iva_8, 2), line)

                    # IVA 31%
                    # sheet.write(row, 22, round(base_imponible_31, 2), line)
                    # sheet.write(row, 23, alic_31, line)
                    # sheet.write(row, 24, round(iva_31, 2), line)

                    # Retenciones (si aplica, aquí puedes dejar en blanco o ajustar)
                    sheet.write(row, 22, '', line)

                    # IGTF
                    # sheet.write(row, 26, round(igtf_amount, 2), line)

                # Dentro de la iteración de las facturas, por cada 'invoice' (solo para ventas)
                if obj.type == 'sale':
                    # Verificar si la factura tiene retención de IVA (directo desde la factura, no de pagos)
                    if invoice.withholding_iva and invoice.withholding_number:
                        total_iva_16_retenido += invoice.withholding_iva

                        i += 1
                        sheet.write(row, 0, i, cell_format_3)  # Número de operación
                        sheet.write(row, 1, invoice.invoice_date, date_line)  # Fecha
                        sheet.write(row, 2, 'Retención', line)  # Tipo de documento
                        sheet.write(row, 3, '', line)  # Número de documento (vacío)
                        sheet.write(row, 4, '', line)  # Número de control (vacío)
                        sheet.write(row, 5, invoice.withholding_number, line)  # Número de comprobante
                        sheet.write(row, 6, invoice.reference_number or invoice.name, line)  # Documento afectado
                        sheet.write(row, 7, invoice.partner_id.name or 'N/A', line)  # Nombre del cliente
                        sheet.write(row, 8, '%s-%s' % (
                            invoice.partner_id.l10n_latam_identification_type_id.l10n_ve_code or 'N/A',
                            invoice.partner_id.vat or 'N/A'
                        ), line)  # RIF
                        sheet.write(row, 9, '', line)  # Total ventas incluyendo IVA (vacío)
                        sheet.write(row, 10, '', line)  # Base imponible (vacío)

                        # Celdas adicionales vacías (ajusta si necesitas)
                        for col in range(11, 28):
                            sheet.write(row, col, '', line)

                        # Columna de IVA retenido
                        sheet.write(row, 28, abs(invoice.withholding_iva), line)
                        sheet.write(row, 29, '', line)  # IGTF (vacío)

                        row += 1  # Avanzar a la siguiente fila

                    else:
                        fi += 1

                    i += 1

                    # contador de la factura
                    sheet.write(row, 0, i, line)
                    # codigo fecha
                    sheet.write(row, 1, invoice.invoice_date or 'FALSE', date_line)
                    # tipo de documento
                    
                    if invoice.move_type == 'out_invoice' and not invoice.debit_origin_id:
                        sheet.write(row, 2, 'Factura', line)
                    elif invoice.move_type == 'out_invoice' and invoice.debit_origin_id:
                        sheet.write(row, 2, 'Nota de Debito', line)
                    elif invoice.move_type == 'out_refund' and not invoice.debit_origin_id:
                        sheet.write(row, 2, 'Nota de Credito', line)
                    elif invoice.move_type == 'in_invoice':
                        sheet.write(row, 2, 'Factura', line)
                    elif invoice.move_type == 'in_refund' and not invoice.debit_origin_id:
                        sheet.write(row, 2, 'Nota de Credito', line)
                    elif invoice.move_type == 'in_refund' and invoice.debit_origin_id:
                        sheet.write(row, 2, 'Nota de Debito', line)

                    # Número de Documento
                    sheet.write(row, 3, invoice.reference_number or invoice.name or invoice.ref or '', line)
                    # Número de Control
                    sheet.write(row, 4, invoice.l10n_ve_document_number or 'FALSE', line)
                    # Ticket FiscalL                                                
                    sheet.write(row, 3, invoice.ref or 'FALSE', line)
                    # Factura cancelada
                    if invoice.state == 'cancel':
                        sheet.write(row, 5, '', line)
                        sheet.write(row, 6, '', line)
                        sheet.write(row, 7, 'ANULADA', line)

                    
                    else:
                        sheet.write(row, 5, '', line)
                        # Número Factura Afectada si es de debito o credito
                        if invoice.move_type == 'out_refund':
                            if invoice.reversed_entry_id:
                                sheet.write(row, 6, invoice.reversed_entry_id.name or invoice.reversed_entry_id.reference_number, line)
                            else:
                                sheet.write(row, 6, '', line)
                        elif invoice.debit_origin_id:
                            sheet.write(row, 6, invoice.debit_origin_id.name, line)
                        else:
                            sheet.write(row, 6, '', line)
                        # nombre del partner
                        sheet.write(row, 7, invoice.partner_id.name or 'FALSE', line)
                        # Rif del cliente
                        sheet.write(row, 8, '%s-%s' % (invoice.partner_id. \
                            l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                            invoice.partner_id.vat or 'FALSE'), line)

                        # Total Ventas Bs.Incluyendo IVA
                        if invoice.state != 'cancel':
                            sheet.write(row, 9, round(invoice.amount_total_bs,2) if invoice.move_type == 'out_invoice' else round(invoice.amount_total_bs * -1 ,2) , line)
                        else:
                            sheet.write(row, 9, invoice.amount_untaxed_signed, line)
                        
                        #VENTAS POR CUENTAS DE TERCEROS
                        
                        sheet.write(row, 10, '', line)  
                        sheet.write(row, 11, '', line)
                        sheet.write(row, 12, '', line)
                        sheet.write(row, 13, '', line)

                        
                        #############################

                        # Inicialización de valores
                        base_exento = 0.00
                        base_imponible_16 = 0.00
                        base_imponible_8 = 0.00
                        iva_16 = 0.00
                        iva_8 = 0.00

                        alic_16 = ''
                        alic_8 = ''

                        # Tasa de cambio y factor
                        tasa_cambio = invoice.tax_day if invoice.currency_id.name == 'USD' else 1
                        factor = -1 if invoice.move_type in ['out_refund', 'in_refund'] else 1

                        # Recorrer líneas de la factura para calcular bases imponibles
                        for inv_line in invoice.invoice_line_ids:
                            line_base = inv_line.price_subtotal * tasa_cambio * factor

                            if not inv_line.tax_ids:
                                # Si la línea no tiene impuestos, es exenta
                                base_exento += line_base
                                continue

                            for tax in inv_line.tax_ids:
                                if tax.amount == 16.0:
                                    base_imponible_16 += line_base
                                    alic_16 = '16%'
                                elif tax.amount == 8.0:
                                    base_imponible_8 += line_base
                                    alic_8 = '8%'
                                # elif tax.amount == 31.0:
                                #     base_imponible_31 += line_base
                                #     alic_31 = '31%'

                        # Recorrer líneas contables para calcular el IVA
                        for move_line in invoice.line_ids:
                            if move_line.tax_line_id:
                                tax = move_line.tax_line_id
                                # tax_amount = move_line.balance * tasa_cambio * factor

                                if tax.amount == 16.0:
                                    iva_16 += base_imponible_16 * 0.16
                                elif tax.amount == 8.0:
                                    iva_8 += base_imponible_8 * 0.08
                                # elif tax.amount == 31.0:
                                #     iva_31 += base_imponible_31 * 0.31

                        # Acumuladores por tipo de cliente
                        if invoice.partner_id.l10n_latam_identification_type_id.is_vat:  # Contribuyente
                            total_base_exento_contribuyente += base_exento
                            total_base_imponible_contribuyente_16 += base_imponible_16
                            total_iva_contribuyente_16 += iva_16
                            total_base_imponible_contribuyente_8 += base_imponible_8
                            total_iva_contribuyente_8 += iva_8

                            # Imprimir en columnas correspondientes (Contribuyente)
                            sheet.write(row, 14, round(base_exento, 2), line)
                            sheet.write(row, 15, round(base_imponible_16, 2), line)
                            sheet.write(row, 16, alic_16, line)
                            sheet.write(row, 17, round(iva_16, 2), line)
                            sheet.write(row, 18, round(base_imponible_8, 2), line)
                            sheet.write(row, 19, alic_8, line)
                            sheet.write(row, 20, round(iva_8, 2), line)

                            # Vaciar celdas No Contribuyentes
                            for col in range(21, 28):
                                sheet.write(row, col, '', line)

                        else:  # No contribuyente
                            total_base_exento_no_contribuyente += base_exento
                            total_base_imponible_no_contribuyente_16 += base_imponible_16
                            total_iva_no_contribuyente_16 += iva_16
                            total_base_imponible_no_contribuyente_8 += base_imponible_8
                            total_iva_no_contribuyente_8 += iva_8

                            # Imprimir en columnas correspondientes (No Contribuyente)
                            sheet.write(row, 14, '', line)
                            sheet.write(row, 15, '', line)
                            sheet.write(row, 16, '', line)
                            sheet.write(row, 17, '', line)
                            sheet.write(row, 18, '', line)
                            sheet.write(row, 19, '', line)
                            sheet.write(row, 20, '', line)

                            sheet.write(row, 21, round(base_exento, 2), line)
                            sheet.write(row, 22, round(base_imponible_16, 2), line)
                            sheet.write(row, 23, alic_16, line)
                            sheet.write(row, 24, round(iva_16, 2), line)
                            sheet.write(row, 25, round(base_imponible_8, 2), line)
                            sheet.write(row, 26, alic_8, line)
                            sheet.write(row, 27, round(iva_8, 2), line)

                        # # IGTF (si aplica)
                        # sheet.write(row, 28, '', line)  # Retención IVA (se llena después)
                        # sheet.write(row, 29, '', line)  # IGTF
                row += 1

            if len(retenciones) > 0 and obj.type == 'sale':
                for reten in sorted(retenciones, key=lambda x: x.date):
                    total_iva_16_retenido += reten.amount
                    i += 1
                    # contador de la factura
                    sheet.write(row, 0, i, line)
                    # codigo fecha
                    sheet.write(row, 1, reten.date or 'FALSE', date_line)
                    # tipo de documento
                    sheet.write(row, 2, 'Retención', line)

                    sheet.write(row, 3, '', line)
                    sheet.write(row, 4, '', line)
                    # Numero de comrpobante
                    sheet.write(row, 5, reten.withholding_number, line)
                    # Documento afectado
                    if len(reten.reconciled_invoice_ids) > 1:
                        sheet.write(row, 6, reten.reconciled_invoice_ids[0].name or reten.reconciled_invoice_ids[0].reference_number, line)
                    else:
                        sheet.write(row, 6, reten.reconciled_invoice_ids.name, line)
                    # nombre del partner
                    sheet.write(row, 7, reten.move_id.partner_id.name or 'FALSE', line)
                    # Rif del cliente
                    sheet.write(row, 8, '%s-%s' % (reten.move_id.partner_id. \
                        l10n_latam_identification_type_id.l10n_ve_code or 'FALSE',
                        reten.move_id.partner_id.vat or 'FALSE'), line)
                    sheet.write(row, 9, invoice.amount_untaxed_signed, line)
                    sheet.write(row, 10, invoice.amount_tax_signed, line)
                    sheet.write(row, 11, '', line)
                    sheet.write(row, 12, '', line)
                    sheet.write(row, 13, '', line)
                    sheet.write(row, 14, '', line)
                    sheet.write(row, 15, '', line)
                    sheet.write(row, 16, '', line)
                    sheet.write(row, 17, '', line)
                    sheet.write(row, 18, '', line)
                    sheet.write(row, 19, '', line)
                    sheet.write(row, 20, '', line)
                    sheet.write(row, 21, '', line)
                    sheet.write(row, 22, '', line)
                    sheet.write(row, 23, '', line)
                    sheet.write(row, 24, '', line)
                    sheet.write(row, 25, '', line)
                    sheet.write(row, 26, '', line)
                    sheet.write(row, 27, '', line)
                    sheet.write(row, 28, reten.amount, line)
                    sheet.write(row, 29, '', line)
                    retenciones.remove(reten)
                    row +=1

            if obj.type == 'sale':
                sheet.write((row), 14, total_base_exento_contribuyente, line_total)
                sheet.write((row), 15, total_base_imponible_contribuyente_16, line_total)
                sheet.write((row), 17, total_iva_contribuyente_16, line_total)
                sheet.write((row), 18, total_base_imponible_contribuyente_8, line_total)
                sheet.write((row), 20, total_iva_contribuyente_8, line_total)

                sheet.write((row), 21, total_base_exento_no_contribuyente, line_total)
                sheet.write((row), 22, total_base_imponible_no_contribuyente_16, line_total)
                sheet.write((row), 24, total_iva_no_contribuyente_16, line_total)
                sheet.write((row), 25, total_base_imponible_no_contribuyente_8, line_total)
                sheet.write((row), 27, total_iva_no_contribuyente_8, line_total)
                
                # RESUMEN DE LOS TOTALES VENTAS
                row +=5
                sheet.merge_range('J%s:M%s' % (str(row+1), str(row+1)), 'RESUMEN GENERAL', cell_format_2)
                sheet.write((row), 13, 'Base Imponible', cell_format_1)
                sheet.write((row), 14, 'Débito fiscal', cell_format_1)
                sheet.write((row), 15, 'IVA Retenido', cell_format_1)
                # sheet.write((row), 16, 'IGTF percibido', cell_format_1)

                sheet.merge_range('J%s:M%s' % (str(row+2), str(row+2)),  'Total Ventas Internas No Gravadas', title_style)
                sheet.write((row+1), 13, round(total_base_exento_contribuyente + total_base_exento_no_contribuyente + total_base_exento_debito - total_base_exento_credito,2), line)
                sheet.write((row+1), 14, '0', line)
                sheet.write((row+1), 15, '0', line)
                sheet.write((row+1), 16, '0', line)
                # sheet.merge_range('J%s:M%s' % (str(row+3), str(row+3)),  'Total Nota de Credito No Gravadas', title_style)
                # sheet.write((row+2), 13, round(total_base_exento_credito,2), line)
                # sheet.write((row+2), 14, '0', line)
                # sheet.write((row+2), 15, '0', line)
                # sheet.write((row+2), 16, '0', line)
                # sheet.merge_range('J%s:M%s' % (str(row+4), str(row+4)),  'Total Nota de Debito No Gravadas', title_style)
                # sheet.write((row+3), 13, round(total_base_exento_debito,2), line)
                # sheet.write((row+3), 14, '0', line)
                # sheet.write((row+3), 15, '0', line)
                # sheet.write((row+3), 16, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row+3), str(row+3)), 'Total Ventas de Exportación ', title_style)
                sheet.write((row+2), 13, '0', line)
                sheet.write((row+2), 14, '0', line)
                sheet.write((row+2), 15, '0', line)
                sheet.write((row+2), 16, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row+4), str(row+4)), 'Total Ventas Internas afectadas sólo alícuota general 16.00', title_style)
                sheet.write((row+3), 13, round(total_base_imponible_contribuyente_16 + total_base_imponible_no_contribuyente_16 - total_nota_credito_16 + total_nota_debito_16,2), line)
                sheet.write((row+3), 14,  total_iva_contribuyente_16 if total_iva_contribuyente_16 else total_iva_no_contribuyente_8, line) #antes estaba total_iva_16
                sheet.write((row+3), 15, total_iva_16_retenido, line)
                sheet.write((row+3), 16, total_iva_16_igtf, line)
                sheet.merge_range('J%s:M%s' % (str(row+5), str(row+5)), 'Total Ventas Internas afectadas sólo alícuota reducida 8.00', title_style)
                sheet.write((row+4), 13, round(total_base_imponible_contribuyente_8 + total_base_imponible_no_contribuyente_8 - total_nota_credito_8 + total_nota_debito_8,2), line)
                sheet.write((row+4), 14, total_iva_8, line)  #total_iva_8
                sheet.write((row+4), 15, '0', line)
                sheet.write((row+4), 16, '0', line)
                # sheet.merge_range('J%s:M%s' % (str(row+8), str(row+8)), 'Total Ventas Internas afectadas  más adicional 31.00', title_style)
                # sheet.write((row+7), 13, '0', line)
                # sheet.write((row+7), 14, '0', line)
                # sheet.write((row+7), 15, '0', line)
                # sheet.write((row+7), 16, '0', line)
                # sheet.merge_range('J%s:M%s' % (str(row+8), str(row+8)), 'Total Notas de Crédito o Devoluciones aplicadas en Ventas 16%', title_style)
                # sheet.write((row+7), 13, total_nota_credito_16, line)
                # sheet.write((row+7), 14, total_nota_credito_iva_16, line)
                # sheet.write((row+7), 15, '', line)
                # sheet.write((row+7), 16, '', line)
                # sheet.merge_range('J%s:M%s' % (str(row+9), str(row+9)), 'Total Notas de Crédito o Devoluciones aplicadas en Ventas 8%', title_style)
                # sheet.write((row+8), 13, total_nota_credito_8, line)
                # sheet.write((row+8), 14, total_nota_credito_iva_8, line)
                # sheet.write((row+8), 15, '', line)
                # sheet.write((row+8), 16, '', line)
                # sheet.merge_range('J%s:M%s' % (str(row+10), str(row+10)), 'Total Notas de Débito o recargos aplicadas en Ventas 16%:', title_style)
                # sheet.write((row+9), 13, total_nota_debito_16, line)
                # sheet.write((row+9), 14, total_nota_debito_iva_16, line)
                # sheet.write((row+9), 15, '', line)
                # sheet.write((row+9), 16, '', line)
                # sheet.merge_range('J%s:M%s' % (str(row+11), str(row+11)), 'Total Notas de Débito o recargos aplicadas en Ventas 8%:', title_style)
                # sheet.write((row+10), 13, total_nota_debito_8, line)
                # sheet.write((row+10), 14, total_nota_debito_iva_8, line)
                # sheet.write((row+10), 15, '', line)
                # sheet.write((row+10), 16, '', line)
                # Calcula el total en la fila 13
                total_row_13 = (
                    total_base_exento_contribuyente + total_base_exento_no_contribuyente +
                    total_base_imponible_contribuyente_16 + total_base_imponible_no_contribuyente_16 +
                    total_base_imponible_contribuyente_8 + total_base_imponible_no_contribuyente_8 +
                    total_base_exento_credito + total_base_exento_debito
                )
                sheet.merge_range('J%s:M%s' % (str(row+6), str(row+6)), 'Total:', title_style)
                sheet.write((row+5), 13, round(total_row_13, 2), line)
                
                if total_iva_contribuyente_16:
                    total_iva_16 = total_iva_contribuyente_16
                else:total_iva_16 = total_iva_no_contribuyente_16
                
                if total_iva_contribuyente_8:
                        total_iva_8 = total_iva_contribuyente_8
                else:total_iva_8 = total_iva_no_contribuyente_8
                
                sheet.write((row+5), 14, (
                    total_iva_16 + total_iva_8 +
                    total_nota_credito_iva_16 + total_nota_credito_iva_8 +
                    total_nota_debito_iva_16 + total_nota_debito_iva_8
                ), line)
                sheet.write((row+5), 15, total_iva_16_retenido, line)
                sheet.write((row+5), 16, total_iva_16_igtf, line)

            # Totales de compras
            else:
                
                sheet.write((row), 12, c_total_base_exento, line_total)
                sheet.write((row), 16, c_total_base_imponible_16, line_total)
                sheet.write((row), 18, c_total_iva_16, line_total)
                sheet.write((row), 19, c_total_base_imponible_8, line_total)
                sheet.write((row), 21, c_total_iva_8, line_total)
                # sheet.write((row), 22, c_total_base_imponible_31, line_total)
                # sheet.write((row), 24, c_total_iva_31, line_total)
                # sheet.write((row), 26, c_total_igtf, line_total)


                row += 5
                sheet.merge_range('J%s:M%s' % (str(row + 1), str(row + 1)), 'RESUMEN GENERAL', cell_format_2)
                sheet.write((row), 13, 'Base Imponible', cell_format_1)
                sheet.write((row), 14, 'Crédito  fiscal', cell_format_1)
                sheet.write((row), 15, 'IVA retenido por el comprador', cell_format_1)
                # sheet.write((row), 16, 'IVA retenido a terceros', cell_format_1)
                # sheet.write((row), 17, 'IGTF', cell_format_1)

                sheet.merge_range('J%s:M%s' % (str(row + 2), str(row + 2)), 'Total Compras Internas NO Gravadas',
                                  title_style)
                sheet.write((row + 1), 13, c_total_base_exento, line)
                sheet.write((row + 1), 14, '0', line)
                sheet.write((row + 1), 15, '0', line)
                # sheet.write((row + 1), 16, '0', line)
                # sheet.write((row + 1), 17, '0', line)
                # sheet.merge_range('J%s:M%s' % (str(row + 3), str(row + 3)), 'Total Notas de Credito NO Gravadas',
                #                   title_style)
                # sheet.write((row + 2), 13, total_base_exento_credito, line)
                # sheet.write((row + 2), 14, '0', line)
                # sheet.write((row + 2), 15, '0', line)
                # sheet.write((row + 2), 16, '0', line)
                # sheet.write((row + 2), 17, '0', line)
                # sheet.merge_range('J%s:M%s' % (str(row + 4), str(row + 4)), 'Total Notas de Debito NO Gravadas',
                #                   title_style)
                # sheet.write((row + 3), 13, total_base_exento_debito, line)
                # sheet.write((row + 3), 14, '0', line)
                # sheet.write((row + 3), 15, '0', line)
                # sheet.write((row + 3), 16, '0', line)
                # sheet.write((row + 3), 17, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row + 3), str(row + 3)), 'Total Compras de Importaciòn', title_style)
                sheet.write((row + 2), 13, '0', line)
                sheet.write((row + 2), 14, '0', line)
                sheet.write((row + 2), 15, '0', line)
                # sheet.write((row + 2), 16, '0', line)
                # sheet.write((row + 2), 17, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row + 4), str(row + 4)),
                                  'Total Compras Internas afectadas sólo alícuota general 16.00', title_style)
                sheet.write((row + 3), 13, round(c_total_base_imponible_16,2), line)
                sheet.write((row + 3), 14, c_total_iva_16, line)
                sheet.write((row + 3), 15, abs(total_iva_16_retenido), line)
                # sheet.write((row + 5), 16, total_iva_16_igtf, line)
                # sheet.write((row + 3), 16, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row + 5), str(row + 5)),
                                  'Total Compras Internas afectadas sólo alícuota reducida 8.00', title_style)
                sheet.write((row + 4), 13, c_total_base_imponible_8, line)
                sheet.write((row + 4), 14, total_iva_8, line)
                sheet.write((row + 4), 15, '0', line)
                # sheet.write((row + 4), 16, '0', line)
                # sheet.write((row + 4), 17, '0', line)
                # sheet.merge_range('J%s:M%s' % (str(row + 8), str(row + 8)),
                #                   'Total Compras Internas afectadas por alícuota general más adicional 31.00', title_style)
                # sheet.write((row + 7), 13, c_total_base_imponible_31, line)
                # sheet.write((row + 7), 14, total_iva_31, line)
                # sheet.write((row + 7), 15, '0', line)
                # sheet.write((row + 7), 16, '0', line)
                # sheet.write((row + 7), 17, '0', line)
                # sheet.merge_range('J%s:M%s' % (str(row+8), str(row+8)), 'Total Notas de Crédito o Devoluciones aplicadas en Compras 16%', title_style)
                # sheet.write((row+7), 13, total_nota_credito_16, line)
                # sheet.write((row+7), 14, total_nota_credito_iva_16, line)
                # sheet.write((row+7), 15, '0', line)
                # sheet.write((row+7), 16, '0', line)
                # sheet.write((row+7), 17, '0', line)
                # sheet.merge_range('J%s:M%s' % (str(row+9), str(row+9)), 'Total Notas de Crédito o Devoluciones aplicadas en Compras 8%', title_style)
                # sheet.write((row+8), 13, total_nota_credito_8, line)
                # sheet.write((row+8), 14, total_nota_credito_iva_8, line)
                # sheet.write((row+8), 15, '0', line)
                # sheet.write((row+8), 16, '0', line)
                # sheet.write((row+8), 17, '0', line)
                # sheet.merge_range('J%s:M%s' % (str(row+11), str(row+11)), 'Total Notas de Crédito o Devoluciones aplicadas en Compras 31%', title_style)
                # sheet.write((row+10), 13, total_nota_credito_31, line)
                # sheet.write((row+10), 14, total_nota_credito_iva_31, line)
                # sheet.write((row+10), 15, '0', line)
                # sheet.write((row+10), 16, '0', line)
                # sheet.write((row + 10), 17, '0', line)
                # sheet.merge_range('J%s:M%s' % (str(row+10), str(row+10)), 'Total Notas de Débito o recargos aplicadas en Compras 16%:', title_style)
                # sheet.write((row+9), 13, total_nota_debito_16, line)
                # sheet.write((row+9), 14, total_nota_debito_iva_16, line)
                # sheet.write((row+9), 15, '0', line)
                # sheet.write((row+9), 16, '0', line)
                # sheet.write((row+9), 17, '0', line)
                # sheet.merge_range('J%s:M%s' % (str(row+11), str(row+11)), 'Total Notas de Débito o recargos aplicadas en Compras 8%:', title_style)
                # sheet.write((row+10), 13, total_nota_debito_8, line)
                # sheet.write((row+10), 14, total_nota_debito_iva_8, line)
                # sheet.write((row+10), 15, '0', line)
                # sheet.write((row+10), 16, '0', line)
                # sheet.write((row+10), 17, '0', line)
                # sheet.merge_range('J%s:M%s' % (str(row+14), str(row+14)), 'Total Notas de Débito o recargos aplicadas en Compras 31%:', title_style)
                # sheet.write((row+13), 13, total_nota_debito_31, line)
                # sheet.write((row+13), 14, total_nota_debito_iva_31, line)
                # sheet.write((row+13), 15, '0', line)
                # sheet.write((row+13), 16, '0', line)
                # sheet.write((row +13), 17, '0', line)
                sheet.merge_range('J%s:M%s' % (str(row+6), str(row+6)), 'Total:', title_style)
                sheet.write((row+5), 13, round(c_total_base_exento + c_total_base_imponible_16 \
                    + c_total_base_imponible_8+total_nota_credito_16+\
                        + total_nota_credito_8 +total_nota_debito_16 + \
                            + total_nota_debito_8 + total_base_exento_credito +\
                                total_base_exento_debito ,2), line)
                sheet.write((row+5), 14, (c_total_iva_16 + c_total_iva_8 + \
                    total_nota_credito_iva_16 + total_nota_credito_iva_8 + \
                        total_nota_debito_iva_16 + total_nota_debito_iva_8), line)
                sheet.write((row+5), 15, abs(total_iva_16_retenido), line)
                # sheet.write((row+6), 16, total_iva_16_igtf, line)
                # sheet.write((row+11), 17, c_total_igtf, line)