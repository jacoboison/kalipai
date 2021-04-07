from odoo import _, api, fields, models, tools

class ResPartner(models.Model):
    _inherit = ['res.partner']
    mx_integritas_claveprov=fields.Char(string="Clave Proveedor",traslate=True)
    mx_integritas_califprov=fields.Char(string="Calificación Proveedor",traslate=True)
    mx_integritas_eanprov=fields.Char(string="GLN (Num. localizaciòn)",traslate=True)
    mx_integritas_no_tienda=fields.Char(string="No tienda",traslate=True)




