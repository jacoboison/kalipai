from odoo import _, api, fields, models, tools
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from pytz import timezone
from pytz import utc
import logging

_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _name = 'account.move'
    _inherit = ['account.move']


    mx_integritas_no_pedido=fields.Char(string="No Pedido",translate=True)
    mx_integritas_fecha_pedido=fields.Datetime(string='Fecha de Pedido')
    mx_integritas_no_recepcion=fields.Char(string="No Recepcion",translate=True)
    mx_integritas_fecha_recepcion=fields.Datetime(string='Fecha de Recepcion')
    mx_integritas_no_factura=fields.Char(string="No Factura",translate=True)
    mx_integritas_fecha_factura=fields.Datetime(string='Fecha de Factura')
    mx_integritas_no_solicitud_pago=fields.Char(string="No Solicitud Pago",translate=True)
    mx_integritas_fecha_no_solic_pago=fields.Datetime(string='Fecha de Solicitud Pago')
    mx_integritas_no_contrarecibo=fields.Char(string="No Contrarecibo",translate=True)
    mx_integritas_fecha_contrarecibo=fields.Date(string='Fecha de Contrarecibo')

    mx_integritas_no_cita=fields.Char(string="No Cita",translate=True)
    mx_integritas_exp=fields.Boolean(string="Extemporaneo",translate=True,default=False)
    mx_integritas_cons=fields.Boolean(string="Consolidado",translate=True,default=False)
    mx_integritas_emp = fields.Selection([
        ('1', 'Cajas'),
        ('2', 'Bultos'),
        ], 'Tipo Empaque')


    def _set_datos_facturacion(self):
        #values=self._l10n_mx_edi_create_cfdi_values()
        edi=self._get_l10n_mx_edi_signed_edi_document()
        values=edi.edi_format_id._l10n_mx_edi_get_invoice_cfdi_values(self)
        print(values)
        #time_invoice = datetime.strptime(self.l10n_mx_edi_time_invoice,DEFAULT_SERVER_TIME_FORMAT).time()
        #values['date'] = datetime.combine(fields.Datetime.from_string(self.invoice_date), time_invoice).strftime('%Y-%m-%dT%H:%M:%S')

        return values

    def _fecha_t(self,fecha,formato):
        localtimezone = timezone('UTC')
        localmoment = localtimezone.localize(fecha, is_dst=None)
        _logger.info(localmoment)

        #partner = self.journal_id.l10n_mx_address_issued_id or self.company_id.partner_id.commercial_partner_id
        partner = self.company_id.partner_id.commercial_partner_id
        tz = self._l10n_mx_edi_get_cfdi_partner_timezone(partner)

        # Check the TZ should be forced for the current journal
        tz_force = self.env['ir.config_parameter'].sudo().get_param(
            'l10n_mx_edi_tz_%s' % self.journal_id.id, default=None)
        if tz_force:
            tz = timezone(tz_force)
        _logger.info(tz_force)

        utcmoment = localmoment.astimezone(tz)
        _logger.info(utcmoment)
        return utcmoment.strftime(formato)

    def _get_articulos(self):
        no_item=0
        no_art=0
        values={}
        for line in self.invoice_line_ids.filtered('price_subtotal'):
            no_item=no_item+1
            no_art=no_art+(line.quantity)
        values['no_item']=no_item
        values['no_art']=no_art

        return values



    def _set_datos_pedrem(self):
        values={}
        for record in self:
            values['no_pedido']=record.mx_integritas_no_pedido
            values['fecha_pedido']=record.mx_integritas_fecha_pedido
            values['no_recepcion']=record.mx_integritas_no_recepcion
            values['fecha_recepcion']=record.mx_integritas_fecha_recepcion
            if(len(record.mapped('invoice_line_ids.sale_line_ids.order_id.client_order_ref'))>0):
                values['no_pedido']=record.mapped('invoice_line_ids.sale_line_ids.order_id.client_order_ref')[0]
                #record.mx_integritas_no_pedido_auto=record.mapped('invoice_line_ids.sale_line_ids.order_id.client_order_ref')[0]
                #record.mx_integritas_hide_no_pedido_auto=True
            if(len(record.mapped('invoice_line_ids.sale_line_ids.order_id.date_order'))>0):
                values['fecha_pedido']=record.mapped('invoice_line_ids.sale_line_ids.order_id.date_order')[0]
                #record.mx_integritas_fecha_pedido_auto=record.mapped('invoice_line_ids.sale_line_ids.order_id.date_order')[0]
                #record.mx_integritas_hide_fecha_pedido_auto=True
            if(len(record.mapped('invoice_line_ids.sale_line_ids.order_id.picking_ids.mx_integritas_refprov'))>0):
                values['no_recepcion']=record.mapped('invoice_line_ids.sale_line_ids.order_id.picking_ids.mx_integritas_refprov')[0]
                #record.mx_integritas_no_recepcion_auto=record.mapped('invoice_line_ids.sale_line_ids.order_id.picking_ids.mx_integritas_refprov')[0]
                #record.mx_integritas_hide_no_recepcion_auto=True
            if(len(record.mapped('invoice_line_ids.sale_line_ids.order_id.picking_ids.scheduled_date'))>0):
                values['fecha_recepcion']=record.mapped('invoice_line_ids.sale_line_ids.order_id.picking_ids.scheduled_date')[0]
                #record.mx_integritas_fecha_recepcion_auto=record.mapped('invoice_line_ids.sale_line_ids.order_id.picking_ids.scheduled_date')[0]
                #record.mx_integritas_hide_fecha_recepcion_auto=True

            return values
                
                   

    
    def _total_impuesto(self):
        monto_ieps=0.0
        monto_iva=0.0
        monto_otro_imp=0.0
        tasa_iva=''
        tasa_ieps=''
        monto_iva_t=0
        monto_iva_r=0
        values={}

        for inv in self:
            for line in inv.invoice_line_ids.filtered('price_subtotal'):
                price = line.price_unit * (1.0 - (line.discount or 0.0) / 100.0)
                taxes_line = line.tax_ids


                print("DEMO Columna")
                print(price)
                taxes_line = taxes_line.filtered(
                    lambda tax: tax.amount_type != 'group') + taxes_line.filtered(
                        lambda tax: tax.amount_type == 'group').mapped('children_tax_ids')
                tax_line = {tax['id']: tax for tax in taxes_line.compute_all(
                    price, line.currency_id, line.quantity, line.product_id, line.partner_id)['taxes']}
                for tax in taxes_line.filtered(lambda r: r.l10n_mx_tax_type != 'Exento'):
                    for li in tax.invoice_repartition_line_ids:
                        if li.repartition_type=='tax':
                            etiq=li
                    
                    if (etiq.tag_ids.name=='IVA'):
                        print("IVA IVA->")
                        monto_iva=monto_iva+(tax.amount / 100 * float("%.2f" % line.price_subtotal))
                        tasa_iva=tasa_iva+'{0:.2f}'.format(tax.amount)+','
                        if(tax.amount>=0):
                            monto_iva_t=monto_iva+(tax.amount / 100 * float("%.2f" % line.price_subtotal))
                        else:
                            monto_iva_r=monto_iva+(tax.amount / 100 * float("%.2f" % line.price_subtotal))
                    if (etiq.tag_ids.name=='IEPS'):
                        print("IEPS->")
                        monto_ieps=monto_ieps+(tax.amount / 100 * float("%.2f" % line.price_subtotal))
                        tasa_ieps=tasa_ieps+'{0:.2f}'.format(tax.amount)+','
                    if(etiq.tag_ids.name!='IVA' and tax.tag_ids.name!='IEPS'):
                        monto_otro_imp=monto_otro_imp+(tax.amount / 100 * float("%.2f" % line.price_subtotal))

            #inv.mx_integritas_montoiva=monto_iva
            #inv.mx_integritas_montoieps=monto_ieps
            #inv.mx_integritas_monto_otros_imp=monto_otro_imp
            if tasa_iva=='':
                tasa_iva='0.00'
            else:
                tasa_iva=tasa_iva[:-1]
            if tasa_ieps=='':
                tasa_ieps='0.00'
            else:
                tasa_ieps=tasa_ieps[:-1]
            values['montoiva']='{0:.2f}'.format(monto_iva)
            values['monto_ieps']='{0:.2f}'.format(monto_ieps)
            values['monto_otro_imp']=monto_otro_imp
            values['tasa_iva']=tasa_iva
            values['tasa_ieps']=tasa_ieps
            values['monto_iva_t']='{0:.2f}'.format(monto_iva_t)
            values['monto_iva_r']='{0:.2f}'.format(monto_iva_r)
            return values

    def lineaDetalleWalmart1(self):
        detalle=''
        for inv in self:
            for line in inv.invoice_line_ids.filtered('price_subtotal'):
                detalle=detalle+'[D1F_Detalle]||'+line.product_id.default_code+'|'+'{0:.0f}'.format(line.quantity)+'||'+line.product_uom_id.name+'|'+line.name+'|'+'{0:.2f}'.format(line.price_unit)+'|'+'{0:.2f}'.format(line.price_total)+'|||||||||||||||||||||||\n'

        return detalle

    def lineaDetalleWalmart2(self):
        detalle=''
        for inv in self:
            for line in inv.invoice_line_ids.filtered('price_subtotal'):
                detalle=detalle='[D1C_Detalle]|||||||||||||'+'{0:.0f}'.format(line.product_uom_id.factor_inv)+'||'+'{0:.0f}'.format(line.quantity)+'|'+'{0:.2f}'.format(line.price_subtotal)+'|'+'{0:.2f}'.format(line.price_total)+'||||||||||||||||'+str(line._total_impuesto()['tasa_iva'])+'|'+str(line._total_impuesto()['montoivalinea'])+'||||||||||||||||||||||||||||||||||||||||||||||||\n'
        return detalle

    def lineaDetalleChedraui1(self):
        detalle=''
        for inv in self:
            for line in inv.invoice_line_ids.filtered('price_subtotal'):
                detalle=detalle+'[D1F_Detalle]||'+line.product_id.default_code+'|'+'{0:.0f}'.format(line.quantity)+'||'+line.product_uom_id.name+'|'+'|'+'{0:.2f}'.format(line.price_unit)+'|'+'{0:.2f}'.format(line.price_total)+'|||||||||||||||||||||||\n'

        return detalle

    def lineaDetalleChedraui2(self):
        detalle=''
        for inv in self:
            for line in inv.invoice_line_ids.filtered('price_subtotal'):
                detalle=detalle='[D1C_Detalle]|||||||||||||'+'{0:.0f}'.format(line.product_uom_id.factor_inv)+'||'+'{0:.0f}'.format(line.quantity)+'|'+'{0:.2f}'.format(line.price_subtotal)+'|'+'{0:.2f}'.format(line.quantity*line.price_unit)+'|'+line._desc_chedraui()+str(line._total_impuesto()['tasa_iva'])+'|'+str(line._total_impuesto()['montoivalinea'])+'||||||||||||||||||||||||||||||||||||||||||||||||\n'
        return detalle

    def _desc_chedraui(self):
        values={}
        seq=''
        for inv in self:
            for line in inv.invoice_line_ids.filtered('price_subtotal'):
                descs=line._descuentos()
                _logger.info(descs)
                for d in descs:
                    values[d['motivo']]=d

        cont=1
        for clave in values:
            valor=values[clave]
            _logger.info(valor)
            if cont>=5:
                break

            _logger.info(valor['porc'])
            _logger.info(valor['motivo'])
            _logger.info(valor['monto'])
            seq=seq+str(valor['porc'])+'|'+str(valor['motivo'])+'|'+str(valor['monto'])+'|'
            cont=cont+1

        while cont<=5:
            seq=seq+'0|0|0|'
            cont=cont+1

        return seq

    def format_dato(self,cad,med):
        largo=len(cad)
        dig_req=med-largo
        digitos_extra=''
        for e in range(dig_req):
            digitos_extra=digitos_extra+'0'
        return digitos_extra+cad







class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'
    #mx_integritas_montoivalinea=fields.Float(string='IVA',compute='_total_impuesto')
    #mx_integritas_montoiepslinea=fields.Float(string='IEPS',compute='_total_impuesto')

    print("Linea Factura")
    
    def get_proddata(self,cadena):
        for line in self:
            datos = self.env['mx_integritas_addendas.addendaprod'].search([('product_id','=',line.product_id.id),('name','=',cadena)])
            if not datos:
                datos = self.env['mx_integritas_addendas.addendaprod'].search([('product_template_id','=',line.product_id.product_tmpl_id.id),('name','=',cadena)])
        
        return datos
    
    def _total_impuesto(self):
        monto_ieps=0.0
        monto_iva=0.0
        tasa_iva=''
        tasa_ieps=''
        values={}
        for line in self:
            taxes_line = line.tax_ids
            print("DEMO Linea")
  
            for tax in taxes_line.filtered(lambda r: r.l10n_mx_tax_type != 'Exento'):
                for li in tax.invoice_repartition_line_ids:
                    if li.repartition_type=='tax':
                        etiq=li
                
                if (etiq.tag_ids.name=='IVA'):
                    print("IVA Linea->")
                    monto_iva=monto_iva+(tax.amount / 100 * float("%.2f" % line.price_subtotal))
                    tasa_iva='{0:.2f}'.format(tax.amount)
                if (etiq.tag_ids.name=='IEPS'):
                    print("IEPS Linea->")
                    monto_ieps=monto_ieps+(tax.amount / 100 * float("%.2f" % line.price_subtotal))
                    tasa_ieps='{0:.2f}'.format(tax.amount)
            if tasa_iva=='':
                tasa_iva='0.00'
            if tasa_ieps=='':
                tasa_ieps='0.00'

            values['montoivalinea']='{0:.2f}'.format(monto_iva)
            values['montoiepslinea']='{0:.2f}'.format(monto_ieps)
            values['tasa_iva']=tasa_iva
            values['tasa_ieps']=tasa_ieps

            return values


    def _descuentos(self):
        values=[]
        order=False
        producto=False
        tax=False
        for line in self:
            for lineaped in line.sale_line_ids:
                order=lineaped.order_id
                producto=line.product_id
                tax=line.tax_ids


        lineasDescuento=self.env['sale.order.line'].search([('order_id','=',order.id),('price_unit','<',0),('tax_id','=',tax.ids)])
        for linea_desc in lineasDescuento:
            producto_descuento=linea_desc.product_id
            descuento=self.env['coupon.program'].search([('discount_line_product_id','=',producto_descuento.id)])
            if descuento.reward_type=='discount':
                if descuento.discount_type=='percentage' and descuento.discount_apply_on=='on_order':
                    desc={}
                    desc['monto']='{0:.2f}'.format(abs(linea_desc.price_unit))
                    desc['porc']='{0:.2f}'.format(abs(descuento.discount_percentage))
                    desc['motivo']=descuento.name
                    values.append(desc)

        return values

    def _desc_chedraui(self):
        seq=''
        cont=1
        for line in self:
            descs=line._descuentos()
            for d in descs:
                if cont>=5:
                    break
                seq=seq+str(d['porc'])+'|'+str(d['motivo'])+'|'+d['monto']+'|'
                cont=cont+1

        while cont<=5:
            seq=seq+'0|0|0|'
            cont=cont+1
        return seq








                

