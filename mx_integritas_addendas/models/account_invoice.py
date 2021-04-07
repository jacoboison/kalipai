from odoo import _, api, fields, models, tools

class AccountInvoice(models.Model):
    _name = 'account.move'
    _inherit = ['account.move']


    mx_integritas_no_pedido=fields.Char(string="No Pedido",traslate=True)
    mx_integritas_fecha_pedido=fields.Datetime(string='Fecha de Pedido')
    mx_integritas_no_recepcion=fields.Char(string="No Recepcion",traslate=True)
    mx_integritas_fecha_recepcion=fields.Datetime(string='Fecha de Recepcion')
    mx_integritas_no_factura=fields.Char(string="No Factura",traslate=True)
    mx_integritas_fecha_factura=fields.Datetime(string='Fecha de Factura')
    mx_integritas_no_solicitud_pago=fields.Char(string="No Solicitud Pago",traslate=True)
    mx_integritas_fecha_no_solic_pago=fields.Datetime(string='Fecha de Solicitud Pago')
    mx_integritas_no_contrarecibo=fields.Char(string="No Contrarecibo",traslate=True)
    mx_integritas_fecha_contrarecibo=fields.Date(string='Fecha de Contrarecibo')

    mx_integritas_no_cita=fields.Char(string="No Cita",traslate=True)
    
    mx_integritas_montoiva=fields.Float(string='Total IVA',compute='_total_impuesto')
    mx_integritas_montoieps=fields.Float(string='Total IEPS',compute='_total_impuesto')
    mx_integritas_monto_otros_imp=fields.Float(string='Otros Impuestos',compute='_total_impuesto')


    mx_integritas_no_pedido_auto=fields.Char(string="No Pedido",traslate=True,compute='_set_datos_atomaticos')
    mx_integritas_fecha_pedido_auto=fields.Datetime(string="Fecha de Pedido",traslate=True,compute='_set_datos_atomaticos')
    mx_integritas_no_recepcion_auto=fields.Char(string="No Recepcion",traslate=True,compute='_set_datos_atomaticos')
    mx_integritas_fecha_recepcion_auto=fields.Datetime(string='Fecha de Recepcion',compute='_set_datos_atomaticos')
    
    
    mx_integritas_show_datos_addenda=fields.Boolean(compute='_mostrar_campo',default=True)
    mx_integritas_hide_no_pedido = fields.Boolean(compute='_mostrar_campo',default=False)
    mx_integritas_hide_fecha_pedido = fields.Boolean(compute='_mostrar_campo',default=False)
    mx_integritas_hide_no_recepcion = fields.Boolean(compute='_mostrar_campo',default=False)
    mx_integritas_hide_fecha_recepcion = fields.Boolean(compute='_mostrar_campo',default=False)
    mx_integritas_hide_no_recepcion = fields.Boolean(compute='_mostrar_campo',default=False)
    mx_integritas_hide_no_factura = fields.Boolean(compute='_mostrar_campo',default=False)
    mx_integritas_hide_fecha_factura = fields.Boolean(compute='_mostrar_campo',default=False)
    mx_integritas_hide_no_contrarecibo = fields.Boolean(compute='_mostrar_campo',default=False)
    mx_integritas_hide_fecha_contrarecibo = fields.Boolean(compute='_mostrar_campo',default=False)
    mx_integritas_hide_no_cita = fields.Boolean(compute='_mostrar_campo',default=False)
    
    mx_integritas_hide_no_pedido_auto = fields.Boolean(compute='_set_datos_atomaticos',default=False)
    mx_integritas_hide_fecha_pedido_auto = fields.Boolean(compute='_set_datos_atomaticos',default=False)
    mx_integritas_hide_no_recepcion_auto = fields.Boolean(compute='_set_datos_atomaticos',default=False)
    mx_integritas_hide_fecha_recepcion_auto = fields.Boolean(compute='_set_datos_atomaticos',default=False)


    #mx_integritas_pedidos=fields.Many2many('sale.order.line','sale_order_line_invoice_rel','invoice_line_id','order_line_id','Pedidos')

    
    
    def _mostrar_campo(self):
        for record in self:

            record.mx_integritas_show_datos_addenda=True
            record.mx_integritas_hide_no_pedido=False
            record.mx_integritas_hide_fecha_pedido=False
            record.mx_integritas_hide_no_recepcion=False
            record.mx_integritas_hide_fecha_recepcion=False
            record.mx_integritas_hide_no_factura=False
            record.mx_integritas_hide_no_cita=False

            if(record.mx_integritas_show_datos_addenda):
                addenda=record.partner_id.l10n_mx_edi_addenda.arch_base
                if addenda:
                    if(addenda.find("mx_integritas_no_pedido")<=-1):
                        record.mx_integritas_hide_no_pedido=True
                    if(addenda.find("mx_integritas_fecha_pedido")<=-1):
                        record.mx_integritas_hide_fecha_pedido=True
                    if(addenda.find("mx_integritas_no_recepcion")<=-1):
                        record.mx_integritas_hide_no_recepcion=True
                    if(addenda.find("mx_integritas_fecha_recepcion")<=-1):
                        record.mx_integritas_hide_fecha_recepcion=True
                    if(addenda.find("mx_integritas_no_factura")<=-1):
                        record.mx_integritas_hide_no_factura=True  
                    if(addenda.find("mx_integritas_no_cita")<=-1):
                        record.mx_integritas_hide_no_cita=True                  


    def _set_datos_atomaticos(self):
        
        for record in self:
            record.mx_integritas_hide_no_pedido_auto=False
            record.mx_integritas_hide_fecha_pedido_auto=False
            record.mx_integritas_hide_no_recepcion_auto=False
            record.mx_integritas_hide_fecha_recepcion_auto=False
            record.mx_integritas_no_pedido_auto=False
            record.mx_integritas_fecha_pedido_auto=False
            record.mx_integritas_no_recepcion_auto=False
            record.mx_integritas_fecha_recepcion_auto=False
            if(len(record.mapped('invoice_line_ids.sale_line_ids.order_id.client_order_ref'))>0):
                record.mx_integritas_no_pedido_auto=record.mapped('invoice_line_ids.sale_line_ids.order_id.client_order_ref')[0]
                record.mx_integritas_hide_no_pedido_auto=True
            if(len(record.mapped('invoice_line_ids.sale_line_ids.order_id.date_order'))>0):
                record.mx_integritas_fecha_pedido_auto=record.mapped('invoice_line_ids.sale_line_ids.order_id.date_order')[0]
                record.mx_integritas_hide_fecha_pedido_auto=True
            if(len(record.mapped('invoice_line_ids.sale_line_ids.order_id.picking_ids.mx_integritas_refprov'))>0):
                record.mx_integritas_no_recepcion_auto=record.mapped('invoice_line_ids.sale_line_ids.order_id.picking_ids.mx_integritas_refprov')[0]
                record.mx_integritas_hide_no_recepcion_auto=True
            if(len(record.mapped('invoice_line_ids.sale_line_ids.order_id.picking_ids.note'))>0):    
                record.mx_integritas_fecha_recepcion_auto=record.mapped('invoice_line_ids.sale_line_ids.order_id.picking_ids.scheduled_date')[0]
                record.mx_integritas_hide_fecha_recepcion_auto=True
                
                   

    
    def _total_impuesto(self):
        monto_ieps=0.0
        monto_iva=0.0
        monto_otro_imp=0.0

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
                for tax in taxes_line.filtered(lambda r: r.l10n_mx_cfdi_tax_type != 'Exento'):
                    for li in tax.invoice_repartition_line_ids:
                        if li.repartition_type=='tax':
                            etiq=li
                    
                    if (etiq.tag_ids.name=='IVA'):
                        print("IVA IVA->")
                        monto_iva=monto_iva+(tax.amount / 100 * float("%.2f" % line.price_subtotal))
                    if (etiq.tag_ids.name=='IEPS'):
                        print("IEPS->")
                        monto_ieps=monto_ieps+(tax.amount / 100 * float("%.2f" % line.price_subtotal))
                    if(etiq.tag_ids.name!='IVA' and tax.tag_ids.name!='IEPS'):
                        monto_otro_imp=monto_otro_imp+(tax.amount / 100 * float("%.2f" % line.price_subtotal))

            inv.mx_integritas_montoiva=monto_iva
            inv.mx_integritas_montoieps=monto_ieps
            inv.mx_integritas_monto_otros_imp=monto_otro_imp

class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'
    mx_integritas_montoivalinea=fields.Float(string='IVA',compute='_total_impuesto')
    mx_integritas_montoiepslinea=fields.Float(string='IEPS',compute='_total_impuesto')

    print("Linea Factura")
    
    def _total_impuesto(self):
        monto_ieps=0.0
        monto_iva=0.0
        for line in self:
            taxes_line = line.tax_ids
            print("DEMO Linea")
  
            for tax in taxes_line.filtered(lambda r: r.l10n_mx_cfdi_tax_type != 'Exento'):
                for li in tax.invoice_repartition_line_ids:
                    if li.repartition_type=='tax':
                        etiq=li
                
                if (etiq.tag_ids.name=='IVA'):
                    print("IVA Linea->")
                    monto_iva=monto_iva+(tax.amount / 100 * float("%.2f" % line.price_subtotal))
                if (etiq.tag_ids.name=='IEPS'):
                    print("IEPS Linea->")
                    monto_ieps=monto_ieps+(tax.amount / 100 * float("%.2f" % line.price_subtotal))        
            line.mx_integritas_montoivalinea=monto_iva
            line.mx_integritas_montoiepslinea=monto_ieps