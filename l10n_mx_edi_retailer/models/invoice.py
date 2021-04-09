# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, tools

class AccountInvoice(models.Model):
    _inherit = "account.move"

    def consulta_pedido(self):
    
        for invoice in self:
            for line in invoice.invoice_line_ids:
                for lineaped in line.sale_line_ids:
                    order=lineaped.order_id

        return order

    def format_dato(self,cad,med):
        largo=len(cad)
        dig_req=med-largo
        digitos_extra=''
        for e in range(dig_req):
            digitos_extra=digitos_extra+'0'
        return digitos_extra+cad





