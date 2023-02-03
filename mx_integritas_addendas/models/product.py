from odoo import _, api, fields, models, tools


class ProductTemplate(models.Model):
    _inherit = ['product.template']
    mx_integritas_gln=fields.Char(string='GLN Producto Addenda',related='product_variant_ids.mx_integritas_gln', readonly=False)
    mx_integritas_ref=fields.Char(string='Referencia Producto Addenda',related='product_variant_ids.mx_integritas_ref', readonly=False)

class ProductTemplate(models.Model):
    _inherit = ['product.product']
    mx_integritas_gln=fields.Char(string='GLN Producto Addenda')
    mx_integritas_ref=fields.Char(string='Referencia Producto Addenda')