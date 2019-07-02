


import logging
from datetime import timedelta,date,datetime
from functools import partial


import psycopg2
import pytz
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class ClosedSessionReport(models.AbstractModel):

	_name = 'report.bi_pos_multi_ticket.report_close_session'
	_description = 'Point of Sale Details'

	@api.model
	def get_sale_details(self, date_start=False, date_stop=False, configs=False,sessions=False):
		""" Serialise the orders of the day information

		params: date_start, date_stop string representing the datetime of order
		"""
		if not configs:
			configs = self.env['pos.config'].search([])

		if sessions:
			orders = self.env['pos.order'].search([
				('date_order', '>=', date_start+ ' 00:00:00'),
				('date_order', '<=', date_stop+ ' 23:59:59'),
				('state', 'in', ['paid','invoiced','done']),
				('session_id.state','in', ['closed']),
				('session_id', 'in', sessions.ids),
				('config_id', 'in', configs.ids)])
		if not sessions:
			orders = self.env['pos.order'].search([
				('date_order', '>=', date_start+ ' 00:00:00'),
				('date_order', '<=', date_stop+ ' 23:59:59'),
				('state', 'in', ['paid','invoiced','done']),
				('session_id.state','in', ['closed']),
				('config_id', 'in', configs.ids)])


		user_currency = self.env.user.company_id.currency_id

		total = 0.0
		products_sold = {}
		total_tax = 0.0
		taxes = {}
		mypro = {}
		products = []

		for order in orders:
			if user_currency != order.pricelist_id.currency_id:
				total += order.pricelist_id.currency_id._convert(
					order.amount_total, user_currency, order.company_id, order.date_order or fields.Date.today())
			else:
				total += order.amount_total
			currency = order.session_id.currency_id

			total_tax = total_tax + order.amount_tax
			for line in order.lines:
				product = str(line.product_id.id)
				if product in mypro:
					old_qty = mypro[product]['qty']
					old_subtotal = mypro[product]['price_subtotal']
					mypro[product].update({
					'product_id' :line.product_id.id,
					'product_name' : line.product_id.display_name,
					'qty' : old_qty + line.qty,
					'product' : line.product_id,
					'price_subtotal' : old_subtotal+line.price_subtotal,
					})
				else:
					mypro.update({ product : {
						'product_id' :line.product_id.id,
						'product_name' : line.product_id.display_name,
						'qty' : line.qty,
						'product' : line.product_id,
						'price_subtotal' : line.price_subtotal,
					}})

			products = list(mypro.values())
		st_line_ids = self.env["account.bank.statement.line"].search([('pos_statement_id', 'in', orders.ids)]).ids
		if st_line_ids:
			self.env.cr.execute("""
				SELECT aj.name, sum(amount) total
				FROM account_bank_statement_line AS absl,
					 account_bank_statement AS abs,
					 account_journal AS aj 
				WHERE absl.statement_id = abs.id
					AND abs.journal_id = aj.id 
					AND absl.id IN %s 
				GROUP BY aj.name
			""", (tuple(st_line_ids),))
			payments = self.env.cr.dictfetchall()
		else:
			payments = []
		configs_name = []
		sessions_name =[]
		for i in configs:
			configs_name.append(i.name) 

		for i in sessions:
			sessions_name += str(i.name)

		configss = ', '.join(map(str,configs_name) )
		# start_date = datetime.strptime(date_start,DEFAULT_SERVER_DATETIME_FORMAT).date()
		# end_date = datetime.strptime(date_stop,DEFAULT_SERVER_DATETIME_FORMAT).date()
		return {
			'currency_precision': 2,
			'start_date': date_start,
			'end_date' : date_stop,
			'total_paid': user_currency.round(total),
			'payments': payments,
			'company_name': self.env.user.company_id.name,
			'taxes': float(total_tax),
			'configs_name' : configss,
			'sessions_name': sessions_name,
			'products_data': products,
		}

	@api.multi
	def _get_report_values(self, docids, data=None):
		data = dict(data or {})
		configs = self.env['pos.config'].browse(data['config_ids'])
		sessions = self.env['pos.session'].browse(data['session_ids'])
		data.update(self.get_sale_details(data['date_start'], data['date_stop'], configs,sessions))
		return data
