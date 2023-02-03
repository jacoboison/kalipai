from odoo import fields, models, api, _

class DatosAddendaProd(models.Model):
	_name = 'mx_integritas_addendas.addendaprod'
	_description = 'Datos de addenda para los productos'

	product_id = fields.Many2one('product.product',string='Producto',ondelete='cascade')
	product_template_id = fields.Many2one('product.template',string='Producto',ondelete='cascade')
	name = fields.Selection([('Fresko', 'Fresko'),('Soriana', 'Soriana'),('Walmart', 'Walmart'),('Chedraui', 'Chedraui'),('Sears', 'Sears'),('HEB', 'HEB'),('CasaLey', 'Casa Ley'),('Seven', 'Seven Eleven')],string='Cadena comercial')
	ean = fields.Char(string='Codigo de barras')
	desc = fields.Char(string='Descripción del producto')
