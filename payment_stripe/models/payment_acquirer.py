# -*- coding: utf-8 -*-

from openerp.addons.payment.models.payment_acquirer import ValidationError
from openerp.osv import osv
from openerp.tools.float_utils import float_compare
from openerp.tools.translate import _

import logging
import pprint

_logger = logging.getLogger(__name__)


class PaypalFriendPaymentAcquirer(osv.Model):
    _inherit = 'payment.acquirer'

    def _get_providers(self, cr, uid, context=None):
        providers = super(PaypalFriendPaymentAcquirer, self)._get_providers(cr, uid, context=context)
        providers.append(['paypal_friend', _('Paypal as a Friend')])
        return providers

    def paypal_friend_get_form_action_url(self, cr, uid, id, context=None):
        return '/payment/transfer/feedback'

    def _format_transfer_data(self, cr, uid, context=None):
        company_id = self.pool['res.users'].browse(cr, uid, uid, context=context).company_id.id
        # filter only bank accounts marked as visible
        pending_msg = _('''<div>
            <h3>Please use the following transfer details</h3>
            <h4>payment@zynthian.org</h4>
            (please, send the money as a friend/donation to avoid the fee)<br><br>
            <h4>Communication</h4>
            <p>Please use the order name as communication reference.</p>
            </div>''') 
        return post_msg

    def create(self, cr, uid, values, context=None):
        """ Hook in create to create a default post_msg. This is done in create
        to have access to the name and other creation values. If no post_msg
        or a void post_msg is given at creation, generate a default one. """
        if values.get('provider') == 'paypal_friend' and not values.get('post_msg'):
            values['pending_msg'] = self._format_transfer_data(cr, uid, context=context)
        return super(PaypalFriendPaymentAcquirer, self).create(cr, uid, values, context=context)


class PaypalFriendPaymentTransaction(osv.Model):
    _inherit = 'payment.transaction'

    def _transfer_form_get_tx_from_data(self, cr, uid, data, context=None):
        reference, amount, currency_name = data.get('reference'), data.get('amount'), data.get('currency_name')
        tx_ids = self.search(
            cr, uid, [
                ('reference', '=', reference),
            ], context=context)

        if not tx_ids or len(tx_ids) > 1:
            error_msg = _('received data for reference %s') % (pprint.pformat(reference))
            if not tx_ids:
                error_msg += _('; no order found')
            else:
                error_msg += _('; multiple order found')
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        return self.browse(cr, uid, tx_ids[0], context=context)

    def _transfer_form_get_invalid_parameters(self, cr, uid, tx, data, context=None):
        invalid_parameters = []

        if float_compare(float(data.get('amount', '0.0')), tx.amount, 2) != 0:
            invalid_parameters.append(('amount', data.get('amount'), '%.2f' % tx.amount))
        if data.get('currency') != tx.currency_id.name:
            invalid_parameters.append(('currency', data.get('currency'), tx.currency_id.name))

        return invalid_parameters

    def _transfer_form_validate(self, cr, uid, tx, data, context=None):
        _logger.info('Validated transfer payment for tx %s: set as pending' % (tx.reference))
        return tx.write({'state': 'pending'})
