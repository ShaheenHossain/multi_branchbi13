# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import openerp.addons.decimal_precision as dp
from openerp import api, fields, models, _


class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.price_total','discount_amount','discount_method')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        cur_obj = self.env['res.currency']
        for order in self:
            sums = order_discount =  amount_untaxed = amount_tax = amount_after_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            # order_discount = self._calculate_discount()
            if order.discount_method == 'per':
                order_discount = amount_untaxed * (order.discount_amount / 100)
                if order.order_line:
                    for line in order.order_line:
                        if line.tax_id:
                            
                            final_discount = ((order.discount_amount*line.price_subtotal)/100.0)
                            
                            discount = line.price_subtotal - final_discount
                            
                            taxes = line.tax_id.compute_all(discount, \
                                                order.currency_id,1.0, product=line.product_id, \
                                                partner=order.partner_id)

                            sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))

                amount_after_discount = amount_untaxed - order_discount
                order.update({
                    'amount_untaxed': amount_untaxed,
                    'amount_tax': sums,
                    'amount_total': amount_untaxed + sums - order_discount,
                    'discount_amt' : order_discount, 
                    'amount_after_discount' : amount_after_discount
                })
            elif order.discount_method == 'fix':
                order_discount = order.discount_amount
                if order.order_line:
                    for line in order.order_line:
                        if line.tax_id:
                            final_discount = ((order.discount_amount*line.price_subtotal)/amount_untaxed)
                            discount = line.price_subtotal - final_discount

                            taxes = line.tax_id.compute_all(discount, \
                                                order.currency_id,1.0, product=line.product_id, \
                                                partner=order.partner_id)

                            sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))

                amount_after_discount = amount_untaxed - order_discount

                order.update({
                    'amount_untaxed': amount_untaxed,
                    'amount_tax': sums,
                    'amount_total': amount_untaxed + sums - order_discount,
                    'discount_amt' : order_discount,
                    'amount_after_discount' : amount_after_discount
                })
            else:
                order.update({
                    'amount_untaxed': amount_untaxed,
                    'amount_tax': amount_tax,
                    'amount_total': amount_untaxed + amount_tax ,
                })


    discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method',default='fix')
    discount_amount = fields.Float('Discount Amount',default=0.0)
    discount_amt = fields.Monetary(compute='_amount_all',store=True, string='- Discount', digits_compute=dp.get_precision('Account'), readonly=True)
    amount_after_discount = fields.Monetary(string='Amount After Discount',store=True, readonly=True, compute='_amount_all')


    @api.multi
    def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserWarning(_('Please define an accounting sale journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'reference': self.client_order_ref or self.name,
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'journal_id': journal_id,
            'discount_method': self.discount_method,
            'discount_amount': self.discount_amount,
            'discount_amt': self.discount_amt,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id
        }
        return invoice_vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
