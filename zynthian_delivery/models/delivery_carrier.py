# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from openerp import api, fields, models, _
from openerp.exceptions import UserError, ValidationError
from openerp.tools.safe_eval import safe_eval as eval

_logger = logging.getLogger(__name__)

class DeliveryCarrierExtend(models.Model):
	_inherit = 'delivery.carrier'

	trackingUrl = fields.Char('Tracking URL', help='Carrier Tracking URL')