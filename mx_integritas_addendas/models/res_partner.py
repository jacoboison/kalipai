from odoo import _, api, fields, models, tools

class ResPartner(models.Model):
    _inherit = ['res.partner']
    mx_integritas_claveprov=fields.Char(string="Clave Proveedor",translate=True)
    mx_integritas_califprov=fields.Char(string="Calificación Proveedor",translate=True)
    mx_integritas_eanprov=fields.Char(string="GLN (Num. localizaciòn)",translate=True)
    mx_integritas_no_tienda=fields.Char(string="No tienda",translate=True)
    mx_integritas_eanodooco=fields.Char(string="GLN (Num. localizaciòn) de Emisor addenda.",translate=True)
    mx_integritas_nombrepaaddenda=fields.Char(string="Nombre para addenda",translate=True)




