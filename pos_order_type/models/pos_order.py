# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    order_type = fields.Selection([('customer', "Customer"),
        ('manager', "Manager"),
        ('staff', "Staff")], string="Order For", default='customer', readonly=True)
    authorised_user_id = fields.Many2one('res.users', string="Authorised User",
        copy=False, readonly=True)

    def _order_fields(self, ui_order):
        """Overrided to add custom order types fields to be write in order"""
        vals = super(PosOrder, self)._order_fields(ui_order)
        if ui_order.get('order_type', False):
            vals.update({'order_type': ui_order['order_type']})
        if ui_order.get('authorised_user', False):
            vals.update({'authorised_user_id': ui_order['authorised_user']})
        return vals
