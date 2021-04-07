# -*- coding: utf-8 -*-
from odoo import http

# class MxIntegritasAddendas(http.Controller):
#     @http.route('/mx_integritas_addendas/mx_integritas_addendas/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mx_integritas_addendas/mx_integritas_addendas/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mx_integritas_addendas.listing', {
#             'root': '/mx_integritas_addendas/mx_integritas_addendas',
#             'objects': http.request.env['mx_integritas_addendas.mx_integritas_addendas'].search([]),
#         })

#     @http.route('/mx_integritas_addendas/mx_integritas_addendas/objects/<model("mx_integritas_addendas.mx_integritas_addendas"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mx_integritas_addendas.object', {
#             'object': obj
#         })