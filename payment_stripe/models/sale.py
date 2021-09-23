from openerp import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)

class sale_order_extend(models.Model):
	_inherit = 'sale.order'

# Modify payment transaction status when quotation is confirmed manually (Wire Transfer and Paypal as a Friend)
	@api.multi
	def action_confirm(self):
		#_logger.info('Payment acquirement: '+str(self.payment_acquirer_id.name))
		if self.payment_acquirer_id.name in ["Paypal as a Friend", "Wire Transfer"]:
			tx = self.env['payment.transaction'].search([('id', '=', self.payment_tx_id.id)], limit=1)
			#_logger.info('Reference: '+str(tx.reference))
			tx.state = 'done'
			#_logger.info('Modify payment transaction to DONE status')

		return super(sale_order_extend,self).action_confirm()

# Modify payment transaction status when sale order is cancelled manually (Wire Transfer and Paypal as a Friend)
	@api.multi
	def action_cancel(self):
		#_logger.info('Payment acquirement: '+str(self.payment_acquirer_id.name))
		if self.payment_acquirer_id.name in ["Paypal as a Friend", "Wire Transfer"]:
			tx = self.env['payment.transaction'].search([('id', '=', self.payment_tx_id.id)], limit=1)
			#_logger.info('Reference: '+str(tx.reference))
			tx.state = 'cancel'
			#_logger.info('Modify payment transaction to CANCEL status')

		return super(sale_order_extend,self).action_cancel()

# Modify payment transaction status when cancelled sale order is set to quotation manually 
# (Wire Transfer and Paypal as a Friend)
	@api.multi
	def action_draft(self):
		#_logger.info('Payment acquirement: '+str(self.payment_acquirer_id.name))
		if self.payment_acquirer_id.name in ["Paypal as a Friend", "Wire Transfer"]:
			tx = self.env['payment.transaction'].search([('id', '=', self.payment_tx_id.id)], limit=1)
			#_logger.info('Reference: '+str(tx.reference))
			tx.state = 'pending'
			#_logger.info('Modify payment transaction to PENDING status')

		return super(sale_order_extend,self).action_draft()