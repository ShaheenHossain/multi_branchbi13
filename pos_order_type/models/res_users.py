# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = 'res.users'

    pos_authorisation_code = fields.Char('Authorisation Code', size=32,
                                         help='Authorisation Code used to protect sensible functionality in the Point of Sale')

    @api.one
    @api.constrains('pos_authorisation_code')
    def _check_pin(self):
        users = self.search([('id', '!=', self.id), ('pos_authorisation_code', '=', self.pos_authorisation_code)])
        if users and self.pos_authorisation_code:
            raise UserError(_("The code for POS order authorisation is unique !"))
        if self.pos_authorisation_code and not self.pos_authorisation_code.isdigit():
            raise UserError(_("Authorisation Code can only contain digits"))
