# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
from lxml import etree
from lxml.objectify import fromstring
from odoo import _, api, fields, models, tools
import logging

_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = "account.move"

    
    def _l10n_mx_edi_add_invoice_cfdi_values(self, cfdi_values):
        self.ensure_one()
        
        super()._l10n_mx_edi_add_invoice_cfdi_values(cfdi_values)
        if cfdi_values.get('errors'):
            return
            
        
        ext_retail_values = cfdi_values['detallista'] = {}
        
        if self.x_complement_retailer_data:
            valor_cabecera = (self.x_complement_retailer_data or '|').split('|')
            ext_retail_values['documentStatus'] = valor_cabecera[0].upper()
            
            ext_retail_values['tipo_de_comprobante'] = cfdi_values['tipo_de_comprobante']
            
            mostrar_aab = False
            mostrar_aab = True if self.partner_id.mostrar_aab and self.invoice_payment_term_id else False
            ext_retail_values['mostrar_aab'] = mostrar_aab
            _logger.info(ext_retail_values['mostrar_aab'])
            ext_retail_values['termPago'] = self.invoice_payment_term_id.name if mostrar_aab else ''
            
            lines_product = self.invoice_line_ids.filtered(lambda l: l.product_id)
            
            ##Pedimentos
            customs = set(lines_product.mapped('l10n_mx_edi_customs_number')) - {False}
            pedimentos = False
            if customs:
                pedimentos = set().union(*[x.split(',') for x in customs])
            ext_retail_values['custom'] = pedimentos
            ext_retail_values['pedimentos'] = pedimentos
            
            ##Uso CFDI
            uso_disp = self.l10n_mx_edi_usage not in (False, 'P01')
            uso_cfdi = dict(self._fields['l10n_mx_edi_usage'].selection).get(self.l10n_mx_edi_usage)
            ext_retail_values['uso_disp'] = uso_disp
            ext_retail_values['uso_cfdi'] = uso_cfdi
            
            ##Monto a Texto
            monto_texto = self._l10n_mx_edi_cfdi_amount_to_text()
            ext_retail_values['monto_texto'] = monto_texto
            
            ##Valores PR
            valuespr = self._set_datos_pedrem()
            ext_retail_values['no_pedido'] = valuespr['no_pedido']
            _logger.info(ext_retail_values['no_pedido'])
            ext_retail_values['ReferenceDate'] = valor_cabecera[1] or False
            _logger.info(valor_cabecera[1])
            _logger.info(valor_cabecera)
            
            ##Producto Impuesto
            property_taxes = False
            prod_imp = self.env['product.template']._fields.get('l10n_mx_edi_property_tax')
            if prod_imp:
                property_taxes = set(lines_product.mapped('product_id.l10n_mx_edi_property_tax')) - {False}
            ext_retail_values['property_taxes'] = property_taxes
            
            ##Payment Method CHECK
            check_payment_method = self.l10n_mx_edi_payment_method_id.code == '02'
            payments = self.payment_ids
            ref_payments = []
            if payments:
                for p in payments:
                    ref_payments.append(p.payment_reference)
            ext_retail_values['check_payment_method'] = check_payment_method
            ext_retail_values['ref_payments'] = ref_payments
            
            ##Payment Method Remision
            remision_payment_method = self.l10n_mx_edi_payment_method_id.code == '25'
            ext_retail_values['remision_payment_method'] = remision_payment_method
            ext_retail_values['ref_payments'] = ref_payments
            
            
            
            ##<!-- if this invoice refers to another one for billing merchandise -->
            another_bill_merchandise = (self.l10n_mx_edi_cfdi_origin or '').startswith('05|')
            merchandise_uuids = False
            if another_bill_merchandise:
                merchandise_uuids = self.l10n_mx_edi_cfdi_origin.split('|')[1].split(',')
            
            ext_retail_values['merchandise_uuids'] = merchandise_uuids
            
            ## Partner IV
            partner_iv = self.partner_id.tipo_folio=='IV' or not self.partner_id.tipo_folio
            record_iv = self.name or self.number
            ext_retail_values['partner_iv'] = partner_iv
            ext_retail_values['record_iv'] = record_iv
            
            ##Partner DQ
            partner_dq = self.partner_id.tipo_folio=='DQ'
            record_dq = valor_cabecera[2].lstrip()
            
            ext_retail_values['partner_dq'] = partner_dq
            ext_retail_values['record_dq'] = record_dq
            
            ##Partner atz            
            partner_atz = self.partner_id.tipo_folio=='ATZ'
            record_atz = self.partner_id.mx_integritas_califprov
            
            ext_retail_values['partner_atz'] = partner_atz
            ext_retail_values['record_atz'] = record_atz
            
            ##Invoice Replace
            inv_replace = (self.l10n_mx_edi_cfdi_origin or '').startswith('04|')
            replaceds = False
            if inv_replace:
                self.l10n_mx_edi_cfdi_origin.split('|')[1].split(',')
                replaceds = self.l10n_mx_edi_cfdi_origin.split('|')[1].split(',')
            ext_retail_values['replaceds'] = replaceds
            
            ##Delivery_note
            show_del_note = len(valor_cabecera) >= 3
            received_folios = valor_cabecera[2].split(',')
            ext_retail_values['show_del_note'] = show_del_note
            ext_retail_values['received_folios'] = received_folios
            
            ##Customer o buyer
            ext_retail_values['customer'] = {
                'gln': self.partner_id.mx_integritas_eanprov or self.partner_id.ref or '',
                'text': self.partner_shipping_id.mx_integritas_no_tienda or self.partner_id.mx_integritas_no_tienda
            }
            
            ##Vendedor o seller
            ext_retail_values['seller'] = {
                'gln': self.format_dato(self.partner_id.mx_integritas_eanodooco,13) or '',
                'SELLER_ASSIGNED_IDENTIFIER_FOR_A_PARTY': self.partner_id.tipo_ref_supplier=='nip' or not self.partner_id.tipo_ref_supplier,
                'IEPS_REFERENCE': self.partner_id.tipo_ref_supplier=='ri',
                'dato': self.partner_id.mx_integritas_eanodooco
            }
            
            
            ##Ship to
            ship_to = self.partner_shipping_id
            show_ship_to = self.partner_id.mostrar_shipto
            
            ext_retail_values['show_ship_to'] = show_ship_to
            ext_retail_values['ship_to'] = {
                'ref': ship_to.ref,
                'name': ship_to.name,
                'streetAddressOne': ', '.join([x for x in (ship_to.street, ship_to.l10n_mx_edi_colony) if x])[:35] or False,
                'city': ship_to.city,
                'zip': ship_to.zip,
            }
            
            ##Moneda
            show_currency = self.partner_id.mostrar_currency
            currency_name = self.currency_id.name.upper()
            ext_retail_values['show_currency'] = show_currency
            ext_retail_values['currency_name'] = currency_name
            ext_retail_values['invoice_name'] = self.name
            ext_retail_values['rate'] = cfdi_values["tipo_cambio"]
            
            ##TermPago
            term_pago = self.invoice_payment_term_id.name if self.invoice_payment_term_id else False
            pay_term_period = False
            if term_pago:
                pay_term_period = (self.invoice_date_due - self.invoice_date).days
            
            _logger.info(cfdi_values['descuento'])
            _logger.info(cfdi_values['subtotal'])
            _logger.info(cfdi_values['total'])
            
            percentage_discount = round(100*float(cfdi_values['descuento'] or 0.0)/float(cfdi_values['subtotal']),self.company_id.currency_id.decimal_places)
            paymentTermsEvent = 'DATE_OF_INVOICE' if self.invoice_date == self.invoice_date_due else 'EFFECTIVE_DATE'
            netPaymentTermsType = 'END_OF_MONTH' if self.invoice_payment_term_id.line_ids[-1].delay_type in ('days_after_end_of_month', 'days_after_end_of_next_month') else 'BASIC_NET'
            discountType = 'ALLOWANCE_BY_PAYMENT_ON_TIME' if percentage_discount >= 0 else 'SANCTION'
            discount_perc = '%.*f' % (self.company_id.currency_id.decimal_places, percentage_discount)
            show_payment_method  = self.partner_id.mostrar_term_pago
            
            
            ext_retail_values['show_payment_method'] = show_payment_method
            ext_retail_values['discount_perc'] = discount_perc
            ext_retail_values['netPaymentTermsType'] = netPaymentTermsType
            ext_retail_values['discountType'] = discountType
            ext_retail_values['pay_term_period'] = pay_term_period
            ext_retail_values['paymentTermsEvent'] = paymentTermsEvent
            
            ##OFF INVOICE
            is_off_invoice = valor_cabecera[4]== 'OFF_INVOICE'
            show_seq_number = self.partner_id.mostrar_seq_number
            specialServicesType = valor_cabecera[3].upper()
            
            ext_retail_values['is_off_invoice'] = is_off_invoice
            ext_retail_values['show_seq_number'] = show_seq_number
            ext_retail_values['specialServicesType'] = specialServicesType
            
            ##Bill BLACK
            is_bill_black = valor_cabecera[4]== 'BILL_BACK'
            ext_retail_values['is_bill_black'] = is_bill_black
            
            ##Mostrar Sin Desc Impuestos
            show_sin_desc_imp = self.partner_id.total_sin_descimp
            ext_retail_values['show_sin_desc_imp'] = show_sin_desc_imp
            ext_retail_values['subtotal_desc'] = '{0:.2f}'.format(float(cfdi_values['subtotal']) - float(cfdi_values['descuento'] or 0))
            ext_retail_values['total'] = '{0:.2f}'.format(float(cfdi_values['total']))
            
            
            ext_retail_values['importe_desc'] = '{0:.2f}'.format(float(cfdi_values['descuento'] or 0))
            
            _logger.info(self.amount_tax)
            
            show_importe_impuestos = self.amount_tax >= 0
            show_importe_impuestos_neg = self.amount_tax * -1 != 0
            importe_impuestos = '{0:.2f}'.format(self.amount_tax)
            importe_impuestos_neg = '{0:.2f}'.format(-1 * self.amount_tax)
            
            ext_retail_values['show_importe_impuestos'] = show_importe_impuestos
            ext_retail_values['show_importe_impuestos_neg'] = show_importe_impuestos_neg
            ext_retail_values['importe_impuestos'] = importe_impuestos
            ext_retail_values['importe_impuestos_neg'] = importe_impuestos_neg
            
            
            
            ext_retail_values['identificaciones'] = self.invoice_origin.split(',') if self.invoice_origin else [] 
            
            
            ###Lineas
            lineas_det = []
            
            for line in lines_product:
                lineas_det.append({
                    'gtin': line.product_id.mx_integritas_gln or line.product_id.product_tmpl_id.mx_integritas_gln or line.product_id.barcode or 'N/A',
                    'is_product_baa': line.product_id.tipo_cod_detallista == 'baa',
                    'is_product_saa': line.product_id.tipo_cod_detallista == 'saa',
                    'ide_prod': line.product_id.mx_integritas_ref or line.product_id.product_tmpl_id.mx_integritas_ref or line.product_id.default_code,
                    'language': 'EN' if self.env.context.get('lang', '').startswith('en') else 'ES',
                    'name': line.product_id.name[:35],
                    'uom': line.product_uom_id.name,
                    'cant': '{0:.0f}'.format(line.quantity or 0.0),
                    'grossPrice': '{0:.0f}'.format(line.price_unit or 0.0),
                    'netPrice': '{0:.2f}'.format(line.price_unit*(1-(line.discount/100)) or 0.0),
                    'grossAmount': '{0:.2f}'.format(line.price_unit *  line.quantity or 0.0),
                    'netAmount': '{0:.2f}'.format(line.price_unit*line.quantity*(1-(line.discount/100))  or 0.0),
                
                })
            
            ext_retail_values['lineas_det'] = lineas_det
            
            
            




            
    """def l10n_mx_edi_append_addenda(self, xml_signed):
        for invoice in self:
            if invoice.x_complement_retailer_data:
                print("Ret")
                tree = str(base64.decodestring(xml_signed).decode("utf-8"))
                #print(xml_signed)
                a=tree
                print(a)
                a=str(a).replace("<detallista:detallista","<detallista:detallista xmlns:detallista=\"http://www.sat.gob.mx/detallista\"")
                #a=str(a).replace("\\r\\n","").replace("b'<","<").replace(">'",">")
                #print("")
                #print(a)
                xml_signed = base64.encodestring(bytes(a, 'UTF-8'))
                attachment_id = self.l10n_mx_edi_retrieve_last_attachment()
                attachment_id.write({
                    'datas': xml_signed,
                    'mimetype': 'application/xml'
                })
                return xml_signed
            else:
                print("No retailler")
                super(AccountInvoice, self).l10n_mx_edi_append_addenda(xml_signed)
                
                """

    





