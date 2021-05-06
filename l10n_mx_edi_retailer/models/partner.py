# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, tools

class ResPartner(models.Model):
    _inherit = "res.partner"

    tipo_folio=fields.Selection(selection=[('AAE', 'Cuenta Predial'),
         ('CK', 'Numero de Cheque'),
         ('ACE', 'Número de Remisíon'),
         ('ATZ', 'Número de Aprobacíon'),
         ('AWR', 'Número que se remplaza'),
         ('ON',  'Número de Pedido'),
         ('DQ',  'Folio de Recibo de Mercancias'),
         ('IV',  'Numero de Factura')],
        string="Tipo de Folio")
    tipo_ref_supplier=fields.Selection(selection=[
        ('nip', 'Número Interno Proveedor'),
        ('ri', 'Referencia IEPS')],
        string="Tipo de Tercero")
    mostrar_currency=fields.Boolean(string="Mostrar Seccíon Moneda")