# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo.exceptions import ValidationError
from odoo import api, models, fields, _


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    has_zero_price = fields.Boolean(copy=False, string="Zero Price?")

    @api.constrains('has_zero_price')
    def _check_has_zero_price(self):
        """Check if zero price is already configure for another pricelist"""
        if self.env[self._name].search_count([('has_zero_price', '=', True)]) > 1:
            raise ValidationError(_("You can\'t configure zero price for more than one price list!"))
