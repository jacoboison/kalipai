# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.osv import expression


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    tipo_cod_detallista = fields.Selection(selection=[
        ('baa', 'Buyer as Asigned'),
        ('saa', 'Suppler as Asigned')],string="Clave de Producto detallista")
    