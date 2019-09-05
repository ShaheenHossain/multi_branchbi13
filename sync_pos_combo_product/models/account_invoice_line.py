# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    parent_id = fields.Many2one('product.product', string="Products", copy=False, help="Manage Main Product")
    sub_product_line = fields.Boolean('combo product', copy=False, help="is sub product then true")
    pos_line_name = fields.Char('Line no', copy=False, help="Name of pos order lines")
