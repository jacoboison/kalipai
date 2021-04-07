# -*- coding: utf-8 -*-

from collections import namedtuple
import json
import time
from datetime import date

from itertools import groupby
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter

class Picking(models.Model):
    _name = "stock.picking"
    _inherit = ['stock.picking']

    mx_integritas_refprov=fields.Char(string="Referencia",traslate=True)

    scheduled_date = fields.Datetime(
        'Scheduled Date', compute='_compute_scheduled_date', inverse='_set_scheduled_date', store=True,
        index=True, track_visibility='onchange',
        help="Scheduled time for the first part of the shipment to be processed. Setting manually a value here would set it as expected date for all the stock moves.")

    mx_integritas_sem=fields.Integer(String="Semana",compute='_set_calculo_semana')
    mx_integritas_no_orden_rem=fields.Char(String="no_orden",compute='_set_datos_po')

    mx_integritas_forem=fields.Char(String="Fecha Orden",compute='_set_datos_po')
    
    
    
    def _set_calculo_semana(self):

        for stock in self:
            print(stock.scheduled_date)
            stock.mx_integritas_sem= stock.scheduled_date.isocalendar()[1]

    
    def _set_datos_po(self):

        for stock in self:
	    
            stock.mx_integritas_forem=stock.mapped('backorder_id')