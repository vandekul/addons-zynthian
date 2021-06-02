#******************************************************************************
# Sale Order ODOO
# 
#
#******************************************************************************
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of
# the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For a full copy of the GNU General Public License see the LICENSE.txt file.
# 
#******************************************************************************

from openerp import api, fields, models, _
from openerp.osv import osv

import logging
import pprint
from openerp.http import request
from openerp import http, SUPERUSER_ID

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
	_inherit = "sale.order"

	related_partner_country = fields.Char("Customer Country", related="partner_id.country_id.name", store=True)