# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    sub_product_line_ids = fields.One2many('product.combo', 'product_template_id', string='Sub Products', copy=False)
    is_combo = fields.Boolean('Use as Combo', copy=False)
    pos_notes = fields.Text("Auto-applied Note for Kitchen", translate=True, copy=False)


class PosProductNotes(models.Model):
    _name = "pos.product_notes"
    _description = "POS Product Notes"

    sequence = fields.Integer(string="Sequence", copy=False)
    name = fields.Char(string="Note", copy=False)
    color = fields.Integer('Color Index')
    pos_category_ids = fields.Many2many('pos.category', string='Point of Sale Categories', copy=False,
                                        help='The note will be available for this group of POS categories. '
                                             'Leave the field empty so that the note is available for all POS categories.')


class SubProductCombo(models.Model):
    _name = "product.combo"
    _description = "Product Combo"

    product_template_id = fields.Many2one('product.template', string='Item')
    is_required_product = fields.Boolean('Required Products', copy=False, help="Set boolean for manage required product")
    category_id = fields.Many2one('pos.category', string='Category',
                                  help="Select Category for combo product")
    product_ids = fields.Many2many('product.product', required=True,
                                   string='Product', copy=False, help="Select many product to add in combo")
    no_of_items = fields.Integer('Maximum Number of Items to Select', required=True, default=1, copy=False,
                                 help="Set how many product select in as require products")
    include_all = fields.Boolean('Include all Products', copy=False)
    is_include_in_main_product_price = fields.Boolean('Include in Main Product Price', default=False, copy=False)

    @api.onchange('category_id')
    def onchange_category(self):
        if self.category_id or not self.category_id:
            self.product_ids = [(6, 0, [])]

    @api.onchange('include_all', 'is_required_product')
    def onchange_include_all_products(self):
        self.is_include_in_main_product_price = False
        if self.is_required_product:
            self.is_include_in_main_product_price = True
        if self.include_all:
            if not self.category_id:
                raise UserError(_('Please select catagory to include all product in combo.'))
            self.product_ids = [(6, 0, self.env['product.product'].search([('pos_categ_id', '=', self.category_id.id), ('available_in_pos', '=', True),('is_combo', '=', False), ('type', '!=', 'service')]).ids)]

    @api.model
    def create(self, vals):
        vals.update({'is_include_in_main_product_price' : False})
        if vals.get('is_required_product'):
            vals.update({'is_include_in_main_product_price' : True})
        return super(SubProductCombo, self).create(vals)

    @api.multi
    def write(self, vals):
        vals.update({'is_include_in_main_product_price' : False})
        if vals.get('is_required_product'):
            vals.update({'is_include_in_main_product_price' : True})
        return super(SubProductCombo, self).write(vals)

    @api.multi
    @api.constrains('no_of_items')
    def _check_no_of_items(self):
        for rec in self:
            if rec.no_of_items <= 0:
                raise ValidationError(_('No of items Value cannot be <= 0.'))
