# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date, time, datetime


class pos_config(models.Model):
    _inherit = 'pos.config'

    pos_logo = fields.Binary(string='POS Logo')
     
