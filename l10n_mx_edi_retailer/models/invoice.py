# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
from lxml import etree
from lxml.objectify import fromstring
from odoo import _, api, fields, models, tools

class AccountInvoice(models.Model):
    _inherit = "account.move"


    def l10n_mx_edi_append_addenda(self, xml_signed):
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

    





