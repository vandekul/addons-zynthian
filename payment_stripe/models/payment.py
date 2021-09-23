# coding: utf-8
#******************************************************************************
# PAYMENT STRIPE FOR ODOO
# 
# Copyright (C) 2021 Susanna Fort <susannafm@gmail.com>
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
from openerp.addons.payment.models.payment_acquirer import ValidationError
from openerp.exceptions import UserError
from openerp.tools.safe_eval import safe_eval
from openerp.tools.float_utils import float_round

import logging
import pprint
import requests

from openerp import http, SUPERUSER_ID

_logger = logging.getLogger(__name__)

# Force the API version to avoid breaking in case of update on Stripe side
# cf https://stripe.com/docs/api#versioning
# changelog https://stripe.com/docs/upgrades#api-changelog
STRIPE_HEADERS = {'Stripe-Version': '2016-03-07'}

# The following currencies are integer only, see https://stripe.com/docs/currencies#zero-decimal
INT_CURRENCIES = [
    u'BIF', u'XAF', u'XPF', u'CLP', u'KMF', u'DJF', u'GNF', u'JPY', u'MGA', u'PYGí', u'RWF', u'KRW',
    u'VUV', u'VND', u'XOF'
];


class PaymentAcquirerStripe(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('stripe', 'Stripe')])
    stripe_secret_key = fields.Char(required_if_provider='stripe', groups='base.group_user')
    stripe_publishable_key = fields.Char(required_if_provider='stripe', groups='base.group_user')
    stripe_image_url = fields.Char(
        "Checkout Image URL", groups='base.group_user',
        help="A relative or absolute URL pointing to a square image of your "
             "brand or product. As defined in your Stripe profile. See: "
             "https://stripe.com/docs/checkout")

    def _get_providers(self, cr, uid, context=None):
        providers = super(PaymentAcquirerStripe, self)._get_providers(cr, uid, context=context)
        providers.append(['stripe', 'Stripe'])
        return providers

    def stripe_form_generate_values(self, cr, uid, id, values, context=None):
        base_url = self.pool['ir.config_parameter'].get_param(cr, uid, 'web.base.url')
        acquirer = self.browse(cr, uid, id, context=context)
        stripe_tx_values = dict(values)
        temp_stripe_tx_values = {
            'company': self.company_id.name,
            'amount': values['amount'],  # Mandatory
            'currency': values['currency'] and values['currency'].name or '',  # Mandatory anyway
            'currency_id': values['currency'] and values['currency'].id or '',  # same here
            'address_line1': values.get('partner_address'),  # Any info of the partner is not mandatory
            'address_city': values.get('partner_city'),
            'address_country': values.get('partner_country') and tx_values.get('partner_country').name or '',
            'email': values.get('partner_email'),
            'address_zip': values.get('partner_zip'),
            'name': values.get('partner_name'),
            'phone': values.get('partner_phone'),
        }
        temp_stripe_tx_values['returndata'] = stripe_tx_values.pop('return_url', '')
        stripe_tx_values.update(temp_stripe_tx_values)
        return stripe_tx_values

    def _get_stripe_api_url(self, cr, uid, environment, context=None):
        return 'api.stripe.com/v1'

    def stripe_s2s_form_process(self, cr, uid, data, context=None):
        values = {
            'cc_number': data.get('cc_number'),
            'cc_cvc': int(data.get('cvc')),
            'cc_holder_name': data.get('cc_holder_name'),
            'cc_expiry': data.get('cc_expiry'),
            'cc_brand': data.get('cc_brand'),
            'acquirer_id': int(data.get('acquirer_id')),
            'partner_id': int(data.get('partner_id'))
        }
        return self.pool['payment.method'].create(cr, SUPERUSER_ID, values, context=context)

    def stripe_s2s_form_validate(self, cr, uid, id, data, context=None):
        error = dict()
        error_message = []

        mandatory_fields = ["cc_number", "cvc", "cc_holder_name", "cc_expiry", "cc_brand"]
        # Validation
        for field_name in mandatory_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'

        return False if error else True

class PaymentTransactionStripe(models.Model):
    _inherit = 'payment.transaction'

    def _create_stripe_charge(self, acquirer_ref=None, tokenid=None, email=None):
        api_url_charge = 'https://%s/charges' % (self.acquirer_id._get_stripe_api_url())
        charge_params = {
            'amount': int(self.amount if self.currency_id.name in INT_CURRENCIES else float_round(self.amount * 100, 2)),
            'currency': self.currency_id.name,
            'metadata[reference]': self.reference
        }
        if acquirer_ref:
            charge_params['customer'] = acquirer_ref
        if tokenid:
            charge_params['card'] = str(tokenid)
        if email:
            charge_params['receipt_email'] = email
        r = requests.post(api_url_charge,
                          auth=(self.acquirer_id.stripe_secret_key, ''),
                          params=charge_params,
                          headers=STRIPE_HEADERS)
        return r.json()

    def stripe_s2s_do_transaction(self, cr, uid, id, context=None, **kwargs):
        # TODO: create tx with s2s type
        if len(self) > 1:
            raise ValueError("Expected singleton: %s" % self)
        
        tx = self.browse(cr, uid, id, context=context)
        account = tx.acquirer_id
        reference = tx.reference or "ODOO-%s-%s" % (datetime.datetime.now().strftime('%y%m%d_%H%M%S'), tx.partner_id.id)

        result = self._create_stripe_charge(acquirer_ref=reference, email=self.partner_email)       
        return self._stripe_s2s_validate_tree(result)

    def _stripe_form_get_tx_from_data(self, cr, uid, data, context=None):
        """ Given a data dict coming from stripe, verify it and find the related
        transaction record. """
        reference = data.get('reference')
        if not reference:
            error_msg = _(
                'Stripe: invalid reply received from provider, missing reference. Additional message: %s'
                % data.get('error', {}).get('message', '')
            )
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        tx = self.search([('reference', '=', reference)])
        if not tx:
            error_msg = (_('Stripe: no order found for reference %s') % reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        elif len(tx) > 1:
            error_msg = (_('Stripe: %s orders found for reference %s') % (len(tx), reference))
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return tx[0]

    def _stripe_s2s_validate_tree(self, tx, tree, tries=2):
        if tx.state not in ('draft', 'pending'):
            _logger.info('Stripe: trying to validate an already validated tx (ref %s)', tx.reference)
            return True

        status = tree.get('status')
        if status == 'succeeded':
            tx.write({
                'state': 'done',
                'date_validate': datetime.date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
                'acquirer_reference': tree.get('id'),
            })
            if tree.get('ALIAS') and tx.partner_id and tx.type == 'form_save' and not tx.payment_method_id:
                pm = tx.env['payment.method'].create({
                    'partner_id': tx.partner_id.id,
                    'acquirer_id': tx.acquirer_id.id,
                    'acquirer_ref': tree.get('ALIAS'),
                    'name': tree.get('CARDNO'),
                })
                tx.write({'payment_method_id': pm.id})
            if tx.callback_eval:
                safe_eval(tx.callback_eval, {'self': tx})
            return True
        else:
            error = 'Stripe: feedback error: %(error_code)s: %(error_msg)s' % {
                'error_code': tree.get('error'),
                'error_msg': tree.get('message'),
            }
            _logger.info(error)
            tx.write({
                'state': 'error',
                'state_message': error,
                'acquirer_reference': tree.get('id'),
            })
            return False

    def _stripe_form_get_invalid_parameters(self, cr, uid, tx, data, context=None):
        invalid_parameters = []
        reference = data.get('reference')
        if reference != tx.acquirer_reference:
            invalid_parameters.append(('Reference', reference, tx.acquirer_reference))
        return invalid_parameters

    def _stripe_form_validate(self,  tx):
        return self._stripe_s2s_validate_tree(tx, tree)


class PaymentMethod(models.Model):
    _inherit = 'payment.method'

    def stripe_create(self, cr, uid, values, context=None):
        res = {}
        payment_acquirer = self.pool['payment.acquirer'].browse(cr, uid, values['acquirer_id'])
        url_token = 'https://%s/tokens' % payment_acquirer._get_stripe_api_url()
        url_customer = 'https://%s/customers' % payment_acquirer._get_stripe_api_url()
        if values.get('cc_number'):
            payment_params = {
                'card[number]': values['cc_number'].replace(' ', ''),
                'card[exp_month]': str(values['cc_expiry'][:2]),
                'card[exp_year]': str(values['cc_expiry'][-2:]),
                'card[cvc]': values['cvc'],
            }
            r = requests.post(url_token,
                              auth=(payment_acquirer.stripe_secret_key, ''),
                              params=payment_params,
                              headers=STRIPE_HEADERS)
            token = r.json()
            if token.get('id'):
                customer_params = {
                    'source': token['id']
                }
                r = requests.post(url_customer,
                                  auth=(payment_acquirer.stripe_secret_key, ''),
                                  params=customer_params,
                                  headers=STRIPE_HEADERS)
                customer = r.json()
                res = {
                    'acquirer_ref': customer['id'],
                    'name': 'XXXXXXXXXXXX%s - %s' % (values['cc_number'][-4:], values['cc_holder_name'])
                }
            elif token.get('error'):
                raise UserError(token['error']['message'])

        # pop credit card info to info sent to create
        for field_name in ["cc_number", "cvc", "cc_holder_name", "cc_expiry", "cc_brand"]:
            values.pop(field_name, None)
        return res