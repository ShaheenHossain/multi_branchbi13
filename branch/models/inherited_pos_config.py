# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class pos_config(models.Model):
    _inherit = 'pos.config'

    pos_branch_ids = fields.Many2many('res.branch', id1='user_id', id2='branch_id',string='Branch')   