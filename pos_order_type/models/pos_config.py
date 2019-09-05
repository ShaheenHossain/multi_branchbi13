# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    iface_ordertype = fields.Boolean(string='Order Type', default=True,
        help="Manage pricing as per Order Type.")
