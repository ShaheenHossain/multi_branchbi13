# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from functools import partial


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    parent_id = fields.Many2one('product.product', string="Products", copy=False, help="Manage Main Product")
    sub_product_line = fields.Boolean('combo product', copy=False, help="is sub product then true")


class PosOrder(models.Model):
    _inherit = 'pos.order'

    note_tag_ids = fields.Many2many('pos.product_notes', string="Order Notes", copy=False)

    @api.model
    def _order_fields(self, ui_order):
        """This method is use for add combo product in pos order lines."""
        result = super(PosOrder, self)._order_fields(ui_order)
        result.update({
            'note': ui_order.get('note') or False,
            'note_tag_ids': [(6, 0, [int(l.get('id')) for l in ui_order['custom_notes']] if ui_order.get('custom_notes') else '')]
        })
        product_obj = self.env['product.product']
        process_line = partial(self.env['pos.order.line']._order_line_fields, session_id=ui_order['pos_session_id'])
        product_line = [process_line(l) for l in ui_order['lines']]
        combo_line = []
        for line in product_line:
            if line[2].get('is_combo_line'):
                product_id = product_obj.browse(line[2]['product_id'])
                if product_id.is_combo:
                    for req_product_list in line[2]['req_product_ids']:
                        combo_line.append((0, 0, {'product_id': req_product_list,
                                                  'price_subtotal': 0.00,
                                                  'is_combo_line': True,
                                                  'sub_product_line': True,
                                                  'parent_id': line[2]['product_id'],
                                                  'tax_ids': line[2]['tax_ids'],
                                                  'price_subtotal_incl': 0.00,
                                                  'discount': line[2]['discount'],
                                                  'id': req_product_list,
                                                  'pack_lot_ids': line[2]['pack_lot_ids'],
                                                  'unreq_product_ids': line[2]['unreq_product_ids'],
                                                  'qty': line[2]['qty'],
                                                  'req_product_ids': line[2]['req_product_ids'],
                                                  'price_unit': 0.00,
                                                  'name': line[2]['name'] if line[2].get('name') else product_obj.browse(req_product_list).name}))

                    for unreq_product_list in line[2]['unreq_product_ids']:
                        combo_line.append((0, 0, {'product_id': unreq_product_list,
                            'price_subtotal': 0.00,
                            'is_combo_line': True,
                            'sub_product_line': True,
                            'parent_id': line[2]['product_id'],
                            'tax_ids': line[2]['tax_ids'],
                            'price_subtotal_incl': 0.00,
                            'discount': line[2]['discount'],
                            'id': unreq_product_list,
                            'pack_lot_ids': line[2]['pack_lot_ids'],
                            'unreq_product_ids': line[2]['unreq_product_ids'],
                            'qty': line[2]['qty'],
                            'req_product_ids': line[2]['req_product_ids'],
                            'price_unit': 0.00,
                            'name': line[2]['name'] if line[2].get('name') else product_obj.browse(unreq_product_list).name}))

        if combo_line:
            product_line += combo_line
        result.update({'lines': [process_line(l) for l in product_line] if product_line else False})
        return result

    def _action_create_invoice_line(self, line=False, invoice_id=False):
        """This method in add invoice line in manage parent id & boolean for differentiate to main product."""
        inv_line = {}
        inv_line.update({
            'parent_id': line.parent_id.id,
            'sub_product_line': line.sub_product_line,
            'pos_line_name': line.name,
        })
        return super(PosOrder, self)._action_create_invoice_line(line=line, invoice_id=invoice_id).update(inv_line)
