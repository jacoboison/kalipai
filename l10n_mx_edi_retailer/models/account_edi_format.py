# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools, _
from odoo.tools.xml_utils import _check_with_xsd
from odoo.tools.float_utils import float_round, float_is_zero

import logging
import re
import base64
import json
import requests
import random
import string

from lxml import etree
from lxml.objectify import fromstring
from math import copysign
from datetime import datetime
from io import BytesIO
from zeep import Client
from zeep.transports import Transport
from json.decoder import JSONDecodeError

_logger = logging.getLogger(__name__)


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _l10n_mx_edi_post_invoice_pac(self, invoice, exported):
        

        if invoice.x_complement_retailer_data:
            xml=exported['cfdi_str'].decode("UTF-8")
            xml=xml.replace("xmlns:cce11=\"http://www.sat.gob.mx/ComercioExterior11\"","xmlns:detallista=\"http://www.sat.gob.mx/detallista\"")
            xml=xml.replace(" http://www.sat.gob.mx/ComercioExterior11 http://www.sat.gob.mx/sitio_internet/cfd/ComercioExterior11/ComercioExterior11.xsd"," http://www.sat.gob.mx/detallista http://www.sat.gob.mx/sitio_internet/cfd/detallista/detallista.xsd")
            cfdi_det=xml.encode('UTF-8')
            
            pac_name = invoice.company_id.l10n_mx_edi_pac

            credentials = getattr(self, '_l10n_mx_edi_get_%s_credentials' % pac_name)(invoice)
            if credentials.get('errors'):
                return {
                    'error': self._l10n_mx_edi_format_error_message(_("PAC authentification error:"), credentials['errors']),
                }

            res = getattr(self, '_l10n_mx_edi_%s_sign_invoice' % pac_name)(invoice, credentials,cfdi_det)
            if res.get('errors'):
                return {
                    'error': self._l10n_mx_edi_format_error_message(_("PAC failed to sign the CFDI:"), res['errors']),
                }
        else:
            res = super(AccountEdiFormat, self)._l10n_mx_edi_post_invoice_pac(invoice, exported)

        return res