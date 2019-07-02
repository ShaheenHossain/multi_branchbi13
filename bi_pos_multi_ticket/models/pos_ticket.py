# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from itertools import groupby
from datetime import datetime, timedelta
from functools import partial
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
import odoo.addons.decimal_precision as dp


class PosConfigInherit(models.Model):
	_inherit = 'pos.config'

	digits_serial_no = fields.Integer(string='Sequence Length :',default = 3,required=True)
	prefix_serial_no = fields.Char(string="Prefix :",default = "POS",required=True)
	enable_num_of_invoice =  fields.Boolean(string='Allow multiple prints')
	enable_invoive_prefix =  fields.Boolean(string='Allow Ticket No.')
	number_of_invoice = fields.Integer(string="POS No of Invoice Copy",default = 1,required=True)

	@api.multi
	def write(self, vals):
		result = super(PosConfigInherit, self).write(vals)
		if 'number_of_invoice' in vals:
			if vals['number_of_invoice'] < 1 :
				raise UserError ("Number of print should be more than zero(0).")
		# if 'digits_serial_no' in vals:		
		# 	if vals['digits_serial_no'] < 3 :
		# 		raise UserError ("Ticket number should be three or more than three.")

		return result


class PosSessionInherit(models.Model):
	_inherit = 'pos.session'

	serial_no = fields.Integer(default = 0)
	
	@api.multi
	def action_pos_session_close(self):
		# Close CashBox
		for session in self:
			company_id = session.config_id.company_id.id
			ctx = dict(self.env.context, force_company=company_id, company_id=company_id)
			for st in session.statement_ids:
				if abs(st.difference) > st.journal_id.amount_authorized_diff:
					# The pos manager can close statements with maximums.
					if not self.user_has_groups("point_of_sale.group_pos_manager"):
						raise UserError(_("Your ending balance is too different from the theoretical cash closing (%.2f), the maximum allowed is: %.2f. You can contact your manager to force it.") % (st.difference, st.journal_id.amount_authorized_diff))
				if (st.journal_id.type not in ['bank', 'cash']):
					raise UserError(_("The journal type for your payment method should be bank or cash."))
				st.with_context(ctx).sudo().button_confirm_bank()
		self.with_context(ctx)._confirm_orders()
		self.write({'state': 'closed'})
		self.update({'serial_no' : 0})
		return {
			'type': 'ir.actions.client',
			'name': 'Point of Sale Menu',
			'tag': 'reload',
			'params': {'menu_id': self.env.ref('point_of_sale.menu_point_root').id},
		}



class PosOrderInherit(models.Model):
	_inherit = 'pos.order'

	ticket_number =  fields.Char(string="Ticket :",readonly=True)
	serial_no = fields.Integer(default = 0)

	@api.model
	def _order_fields(self, ui_order):
		process_line = partial(self.env['pos.order.line']._order_line_fields, session_id=ui_order['pos_session_id'])
		# session = self.env['pos.session'].browse(ui_order['pos_session_id'])
		# number = self.session_id.create_sequence(session)
		return {
			'name':         ui_order['name'],
			'user_id':      ui_order['user_id'] or False,
			'session_id':   ui_order['pos_session_id'],
			'lines':        [process_line(l) for l in ui_order['lines']] if ui_order['lines'] else False,
			'pos_reference': ui_order['name'],
			'partner_id':   ui_order['partner_id'] or False,
			'date_order':   ui_order['creation_date'],
			'fiscal_position_id': ui_order['fiscal_position_id'],
			'pricelist_id': ui_order['pricelist_id'],
			'amount_paid':  ui_order['amount_paid'],
			'amount_total':  ui_order['amount_total'],
			'amount_tax':  ui_order['amount_tax'],
			'amount_return':  ui_order['amount_return'],
			'ticket_number' : ui_order['ticket_number'],
		}

	@api.model
	def _process_order(self, pos_order):
		pos_session = self.env['pos.session'].browse(pos_order['pos_session_id'])
		if pos_session.state == 'closing_control' or pos_session.state == 'closed':
			pos_order['pos_session_id'] = self._get_valid_session(pos_order).id
		order = self.create(self._order_fields(pos_order))
		prec_acc = order.pricelist_id.currency_id.decimal_places
		journal_ids = set()
		for payments in pos_order['statement_ids']:
			if not float_is_zero(payments[2]['amount'], precision_digits=prec_acc):
				order.add_payment(self._payment_fields(payments[2]))
			journal_ids.add(payments[2]['journal_id'])

		if pos_session.sequence_number <= pos_order['sequence_number']:
			pos_session.write({'sequence_number': pos_order['sequence_number'] + 1})
			pos_session.refresh()

		if 'serial_no' in pos_order:
			if pos_session.serial_no <= pos_order['serial_no']:
				pos_session.write({'serial_no': pos_order['serial_no'] + 1})
				pos_session.refresh()

		if not float_is_zero(pos_order['amount_return'], prec_acc):
			cash_journal_id = pos_session.cash_journal_id.id
			if not cash_journal_id:
				# Select for change one of the cash journals used in this
				# payment
				cash_journal = self.env['account.journal'].search([
					('type', '=', 'cash'),
					('id', 'in', list(journal_ids)),
				], limit=1)
				if not cash_journal:
					# If none, select for change one of the cash journals of the POS
					# This is used for example when a customer pays by credit card
					# an amount higher than total amount of the order and gets cash back
					cash_journal = [statement.journal_id for statement in pos_session.statement_ids if statement.journal_id.type == 'cash']
					if not cash_journal:
						raise UserError(_("No cash statement found for this session. Unable to record returned cash."))
				cash_journal_id = cash_journal[0].id
			order.add_payment({
				'amount': -pos_order['amount_return'],
				'payment_date': fields.Date.context_today(self),
				'payment_name': _('return'),
				'journal': cash_journal_id,
			})
		return order


