# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.tools import float_is_zero
from odoo.tools.float_utils import float_round as round
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
	pycompat, date_utils
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.exceptions import UserError

class account_invoice(models.Model):
	_inherit = 'account.invoice'

	# Load all unsold PO lines
	@api.onchange('purchase_id')
	def purchase_order_change(self):
		if not self.purchase_id:
			return {}
		if not self.partner_id:
			self.partner_id = self.purchase_id.partner_id.id

		new_lines = self.env['account.invoice.line']
		for line in self.purchase_id.order_line - self.invoice_line_ids.mapped('purchase_line_id'):
			data = self._prepare_invoice_line_from_po_line(line)
			new_line = new_lines.new(data)
			new_line._set_additional_fields(self)
			new_lines += new_line

		self.invoice_line_ids += new_lines
		self.payment_term_id = self.purchase_id.payment_term_id
		self.discount_amount = self.purchase_id.discount_amount
		self.discount_method = self.purchase_id.discount_method
		self.discount_amt =self.purchase_id.discount_amt
		self.env.context = dict(self.env.context, from_purchase_order_change=True)
		self.purchase_id = False
		return {}


	@api.one
	@api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id','discount_amount','discount_method')
	def _compute_amount(self):
		self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
		self.amount_tax = sum(line.amount for line in self.tax_line_ids)
		res = 0.0
		if self.discount_method == 'fix':
			res = self.discount_amount
		elif self.discount_method == 'per':
			res = self.amount_untaxed * (self.discount_amount / 100.0)
		else:
			res = 0.0
		self.discount_amt = res
		sums = 0
		# self.amount_total = self.amount_tax + self.amount_untaxed
		self.amount_after_discount = self.amount_untaxed - self.discount_amt
		amount_total_company_signed = self.amount_total
		amount_untaxed_signed = self.amount_untaxed
		if self.currency_id and self.currency_id != self.company_id.currency_id:
			amount_total_company_signed = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
			amount_untaxed_signed = self.currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
		sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
		self.amount_total_company_signed = amount_total_company_signed * sign
		self.amount_total_signed = self.amount_total * sign
		self.amount_untaxed_signed = amount_untaxed_signed * sign
		if self.discount_method == 'fix':
			if self.invoice_line_ids:
				for line in self.invoice_line_ids:
					if line.invoice_line_tax_ids:
						if self.amount_untaxed:
							final_discount = ((self.discount_amt*line.price_subtotal)/self.amount_untaxed)
							discount = line.price_subtotal - final_discount
							taxes = line.invoice_line_tax_ids.compute_all(discount, self.currency_id, 1.0,
															line.product_id,self.partner_id)
							sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
						else:
							raise Warning("please first deliverd quantity of selected purchase order.")
			self.amount_total = sums + self.amount_untaxed - self.discount_amt
			self.amount_tax = sums
		elif self.discount_method == 'per':
			if self.invoice_line_ids:
				for line in self.invoice_line_ids:
					if line.invoice_line_tax_ids:
						final_discount = ((self.discount_amount*line.price_subtotal)/100.0)
						discount = line.price_subtotal - final_discount
						taxes = line.invoice_line_tax_ids.compute_all(discount, self.currency_id, 1.0,
														line.product_id,self.partner_id)
						sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
			self.amount_total = sums + self.amount_untaxed - self.discount_amt
			self.amount_tax = sums
		else:
			self.amount_total = self.amount_tax + self.amount_untaxed


	@api.onchange('vendor_bill_purchase_id')
	def _onchange_bill_purchase_order(self):
		self.discount_method = self.vendor_bill_purchase_id.purchase_order_id.discount_method
		self.discount_amount = self.vendor_bill_purchase_id.purchase_order_id.discount_amount
		return super(account_invoice, self)._onchange_bill_purchase_order()


	@api.onchange('amount_total')
	def _onchange_amount_total(self):
		for inv in self:
			if float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1:
				pass
				# raise Warning(_('You cannot validate an invoice with a negative total amount. You should create a credit note instead.'))

	discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')],'Discount Method',default='fix')
	discount_amount = fields.Float('Discount Amount',default=0.0)
	discount_amt = fields.Monetary(string='- Discount',store=True, readonly=True, compute='_compute_amount')
	amount_after_discount = fields.Monetary(string='Amount After Discount',store=True, readonly=True, compute='_compute_amount')

	@api.model
	def create(self, vals):
		res = super(account_invoice, self).create(vals)
		res._onchange_invoice_line_ids()
		return res


	@api.onchange('invoice_line_ids','discount_amount','discount_method')
	def _onchange_invoice_line_ids(self):
		taxes_grouped = self.get_taxes_values()
		tax_lines = self.tax_line_ids.filtered('manual')
		for tax in taxes_grouped.values():
			tax_lines += tax_lines.new(tax)
		self.tax_line_ids = tax_lines
		return


	@api.multi
	def get_taxes_values(self):
		tax_grouped = {}
		round_curr = self.currency_id.round
		order_discount = 0.0
		if self.discount_method == 'fix':
			order_discount = self.discount_amount
			# amount_after_discount = self.amount_untaxed - order_discount
			if self.invoice_line_ids:
				for line in self.invoice_line_ids:
					if line.invoice_line_tax_ids:
						final_discount = ((self.discount_amt*line.price_subtotal)/self.amount_untaxed)
						discount = line.price_subtotal - final_discount
						taxes = line.invoice_line_tax_ids.compute_all(discount, self.currency_id, 1.0,
														line.product_id,self.partner_id)['taxes']
						# sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
						for tax in taxes:              
							val = self._prepare_tax_line_vals(line, tax)
							key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
							if key not in tax_grouped:
								tax_grouped[key] = val
								tax_grouped[key]['base'] = round_curr(val['base'])
							else:
								tax_grouped[key]['amount'] += val['amount']
								tax_grouped[key]['base'] += round_curr(val['base'])
		elif self.discount_method == 'per':
			order_discount = self.amount_untaxed * (self.discount_amount / 100)
			# amount_after_discount = self.amount_untaxed - order_discount
			if self.invoice_line_ids:
				for line in self.invoice_line_ids:
					if line.invoice_line_tax_ids:
						final_discount = ((self.discount_amount*line.price_subtotal)/100.0)
						discount = line.price_subtotal - final_discount
						taxes = line.invoice_line_tax_ids.compute_all(discount, self.currency_id, 1.0,
														line.product_id,self.partner_id)['taxes']
						for tax in taxes:                   
							val = self._prepare_tax_line_vals(line, tax)
							key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
							if key not in tax_grouped:
								tax_grouped[key] = val
								tax_grouped[key]['base'] = round_curr(val['base'])
							else:
								tax_grouped[key]['amount'] += val['amount']
								tax_grouped[key]['base'] += round_curr(val['base'])
		else:
			for line in self.invoice_line_ids:
				if not line.account_id:
					continue
				price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
				taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
				for tax in taxes:
					val = self._prepare_tax_line_vals(line, tax)
					key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)
					
					if key not in tax_grouped:
						tax_grouped[key] = val
						tax_grouped[key]['base'] = round_curr(val['base'])
					else:
						tax_grouped[key]['amount'] += val['amount']
						tax_grouped[key]['base'] += round_curr(val['base'])
		return tax_grouped


	@api.model
	def invoice_line_move_line_get(self):
		res = []
		
		for line in self.invoice_line_ids:
			final_discount = 0  
			if not line.account_id:
				continue
			if line.quantity==0:
				continue

			if self.discount_method == 'fix':
				if self.discount_amount != 0.0:
					final_discount = ((self.discount_amt*line.price_subtotal)/self.amount_untaxed)
			elif self.discount_method == 'per':
				if self.discount_amount != 0.0:
					final_discount = ((self.discount_amount*line.price_subtotal)/100.0)
			else:
				final_discount = 0

			tax_ids = []
			for tax in line.invoice_line_tax_ids:
				tax_ids.append((4, tax.id, None))
				for child in tax.children_tax_ids:
					if child.type_tax_use != 'none':
						tax_ids.append((4, child.id, None))
			analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

			move_line_dict = {
				'invl_id': line.id,
				'type': 'src',
				'name': line.name,
				'price_unit': line.price_unit,
				'quantity': line.quantity,
				'price': line.price_subtotal - round(final_discount,2),
				'account_id': line.account_id.id,
				'product_id': line.product_id.id,
				'uom_id': line.uom_id.id,
				'account_analytic_id': line.account_analytic_id.id,
				'analytic_tag_ids': analytic_tag_ids,
				'tax_ids': tax_ids,
				'invoice_id': self.id,
			}
			res.append(move_line_dict)
		return res


class StockMoveInherit(models.Model):
	_inherit = 'stock.move'

	def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id):
		# This method returns a dictonary to provide an easy extension hook to modify the valuation lines (see purchase for an example)
		self.ensure_one()

		active_model = self._context.get('active_model')
		active_id = self._context.get('active_id')

		new_id = self.env[active_model].browse(active_id)

		final_discount = 0
		if active_model == 'purchase.order':
			if new_id.discount_method:
				if new_id.order_line:
					for line in new_id.order_line:
						if line.product_id == self.product_id:
							if new_id.discount_method == 'fix':
								if new_id.discount_amount != 0.0:
									final_discount = ((new_id.discount_amt*line.price_subtotal)/new_id.amount_untaxed)
							elif new_id.discount_method == 'per':
								if new_id.discount_amount != 0.0:
									final_discount = ((new_id.discount_amount*line.price_subtotal)/100.0)
							else:
								final_discount = 0

		if self._context.get('forced_ref'):
			ref = self._context['forced_ref']
		else:
			ref = self.picking_id.name

		if debit_value > 0:
			debit_value = debit_value - final_discount
		if credit_value > 0:
			credit_value = credit_value - final_discount

		debit_line_vals = {
			'name': self.name,
			'product_id': self.product_id.id,
			'quantity': qty,
			'product_uom_id': self.product_id.uom_id.id,
			'ref': ref,
			'partner_id': partner_id,
			'debit': debit_value if debit_value > 0 else 0,
			'credit': -debit_value if debit_value < 0 else 0,
			'account_id': debit_account_id,
		}

		credit_line_vals = {
			'name': self.name,
			'product_id': self.product_id.id,
			'quantity': qty,
			'product_uom_id': self.product_id.uom_id.id,
			'ref': ref,
			'partner_id': partner_id,
			'credit': credit_value if credit_value > 0 else 0,
			'debit': -credit_value if credit_value < 0 else 0,
			'account_id': credit_account_id,
		}

		rslt = {'credit_line_vals': credit_line_vals, 'debit_line_vals': debit_line_vals}
		if credit_value != debit_value:
			# for supplier returns of product in average costing method, in anglo saxon mode
			diff_amount = debit_value - credit_value
			price_diff_account = self.product_id.property_account_creditor_price_difference

			if not price_diff_account:
				price_diff_account = self.product_id.categ_id.property_account_creditor_price_difference_categ
			if not price_diff_account:
				raise UserError(_('Configuration error. Please configure the price difference account on the product or its category to process this operation.'))

			rslt['price_diff_line_vals'] = {
				'name': self.name,
				'product_id': self.product_id.id,
				'quantity': qty,
				'product_uom_id': self.product_id.uom_id.id,
				'ref': ref,
				'partner_id': partner_id,
				'credit': diff_amount > 0 and diff_amount or 0,
				'debit': diff_amount < 0 and -diff_amount or 0,
				'account_id': price_diff_account.id,
			}
		return rslt
