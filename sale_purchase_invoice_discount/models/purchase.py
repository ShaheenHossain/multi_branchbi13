# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    @api.depends('order_line.price_total','discount_amount','discount_method')
    def _amount_all(self):
        for order in self:
            sums = order_discount = amount_untaxed = amount_tax = amount_after_discount = 0.0
            order_discount = order.discount_amt
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            taxes = {}
            if order.discount_amount!=0.0:
                if order.discount_method == 'per':
                    order_discount = amount_untaxed * (order.discount_amount / 100)
                    if order.order_line:
                        for line in order.order_line:
                            if line.taxes_id:

                                final_discount = ((order.discount_amount*line.price_subtotal)/100.0)

                                discount = line.price_subtotal - final_discount

                                taxes = line.taxes_id.compute_all(discount, \
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
                            if line.taxes_id:
                                # final_discount = ((order.discount_amount*line.price_subtotal)/100.0)
                                final_discount = ((order.discount_amount*line.price_subtotal)/amount_untaxed)
                                discount = line.price_subtotal - round(final_discount,2)

                                taxes = line.taxes_id.compute_all(discount, \
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
            

    @api.multi
    def action_view_invoice(self):
        '''
        This function returns an action that display existing vendor bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        '''
        action = self.env.ref('account.action_vendor_bill_template')
        result = action.read()[0]
        create_bill = self.env.context.get('create_bill', False)
        # override the context to get rid of the default filtering
        result['context'] = {
            'type': 'in_invoice',
            'default_purchase_id': self.id,
            'default_currency_id': self.currency_id.id,
            'default_company_id': self.company_id.id,
            'discount_method' : self.discount_method , 
            'discount_amt' : self.discount_amt,
            'discount_amount' : self.discount_amount ,
            'default_amount_untaxed' : self.amount_untaxed,
            'company_id': self.company_id.id
        }
        # choose the view_mode accordingly
        if len(self.invoice_ids) > 1 and not create_bill:
            result['domain'] = "[('id', 'in', " + str(self.invoice_ids.ids) + ")]"
        else:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            # Do not set an invoice_id if we want to create a new bill.
            if not create_bill:
                result['res_id'] = self.invoice_ids.id or False
        result['context']['default_origin'] = self.name
        result['context']['default_reference'] = self.partner_ref
        return result

        
    discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method',default='fix')
    discount_amount = fields.Float('Discount Amount',default=0.0)
    discount_amt = fields.Monetary(compute='_amount_all',store=True,string='- Discount',readonly=True)
    amount_after_discount = fields.Monetary(string='Amount After Discount',store=True, readonly=True, compute='_amount_all')
