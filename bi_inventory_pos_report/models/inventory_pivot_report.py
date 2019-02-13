# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import tools
from odoo import api, fields, models


class inventory_move_line_report(models.Model):
    _name = "inventory.pivot.report"

    warehouse_id = fields.Many2one('stock.warehouse',string="Warehouse")
    source_doc = fields.Char(string="Source Document")
    transfer_no = fields.Char(string="Transfer No")
    date = fields.Date(string="Date")
    product_id = fields.Many2one('product.product',string="Product")
    description = fields.Char(string="Description")
    quantity = fields.Float(string="Qty")
    unit = fields.Many2one('uom.uom',string="Unit")
    cost = fields.Float(string="Cost")
    total_cost = fields.Float(string="Total Cost")

    


class inventory_movement_pivot(models.Model):
    _name = "inventory.movement.report"


    product_id = fields.Many2one('product.product',string="Product")
    description = fields.Char(string="Description")
    opening = fields.Float(string="Opening Balance Qty")
    recieved = fields.Float(string="Received Qty")
    sale_qty = fields.Float(string="Sales Qty")
    adjestment = fields.Float(string="Adjesment Qty")
    uom = fields.Many2one('uom.uom',string="UOM")
    balance = fields.Float(string="Balance")



class pos_line_pivot(models.Model):
    _name = "pos.pivot.report"


    product_id = fields.Many2one('product.product',string="Product")
    description = fields.Char(string="Description")
    
    price = fields.Float(string="Price")
    sale_qty = fields.Float(string="Sales Qty")
    discount = fields.Float(string="Discount%")
    vat = fields.Float(string="VAT")
    net_sales = fields.Float(string="Net Sales Amount")
    total = fields.Float(string="Total")


class pos_fast_move_pivot(models.Model):
    _name = "pos.pivot.fast.moving"


    product_id = fields.Many2one('product.product',string="Product")
    code = fields.Char(string="Code")
    sale_qty = fields.Float(string="Sales Qty")
    price = fields.Float(string="Price")
    gross_price = fields.Float(string="Gross Sale Amount")
    
    discount = fields.Float(string="Discount%")
    vat = fields.Float(string="VAT")
    net_sales = fields.Float(string="Net Sales Amount")
    



    

    
