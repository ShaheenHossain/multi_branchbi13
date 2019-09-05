# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    order_type = fields.Selection([('customer', "Customer"),
        ('manager', "Manager"),
        ('staff', "Staff")], string="Order Type", readonly=True)
    authorised_user_id = fields.Many2one('res.users', string="Authorised User", readonly=True)

    def _select(self):
        return super(PosOrderReport, self)._select() + """,
            s.authorised_user_id AS authorised_user_id,
            s.order_type AS order_type
        """

    def _group_by(self):
        return super(PosOrderReport, self)._group_by() + """,
            s.authorised_user_id,
            s.order_type
        """
