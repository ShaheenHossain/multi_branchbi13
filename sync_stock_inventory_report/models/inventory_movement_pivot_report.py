# -*- coding: utf-8 -*-
# Part of Synconics. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class InventoryMovementPivot(models.Model):
    _name = "inventory.movement.pivot"
    _rec_name = 'product_id'
    _description = "Inventory Movement Pivot"

    product_id = fields.Many2one('product.product',string="Product")
    product_categ_id = fields.Many2one('product.category',string="Product Category")
    uom_id = fields.Many2one('uom.uom',string="UOM")
    initial_qty = fields.Float(string="Open Balance")
    delivered_qty = fields.Float(string="Sales")
    received_qty = fields.Float(string="Transfer In")
    internal_transfer = fields.Float(string="Transfer Out")
    adjustment = fields.Float(string="Adjesment Qty")
    balance_qty = fields.Float(string="Balance")

