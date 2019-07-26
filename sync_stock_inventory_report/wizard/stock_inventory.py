# -*- coding: utf-8 -*-
# Part of Synconics. See LICENSE file for full copyright and licensing details.

import xlwt
import base64
import pytz
from io import BytesIO
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, ustr


class StockInventoryReport(models.TransientModel):
    _name = "stock.inventory.report"
    _description = 'Stock Inventory Analysis'

    available_in_pos = fields.Boolean(string="Available in POS")
    from_date = fields.Datetime(string="From Date", default=lambda l: fields.Datetime.now() + relativedelta(day=1))
    to_date = fields.Datetime(string="To Date", default=lambda l: fields.Datetime.now() + relativedelta(day=1, months=+1, days=-1))
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.user.company_id.id)
    location_ids = fields.Many2many('stock.location', string="Location")
    filter_by = fields.Selection([('product', 'Product'), ('category', 'Product Category')], required=True, default='product')
    product_ids = fields.Many2many('product.product', string="Product")
    product_categ_ids = fields.Many2many('product.category', string="Product Category")
    data = fields.Char('Name', readonly=True)
    name = fields.Binary('Stock Inventory', readonly=True)
    pdf_report_data = fields.Binary('Stock Inventory', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse',string="Warehouse",required = True)

    @api.onchange('filter_by')
    def onchange_filter_by(self):
        self.product_categ_ids = False
        self.product_ids = False

    @api.multi
    def get_date_as_per_user_timezone(self, convert_date):
        dt = False
        user_tz = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        if convert_date and user_tz:
            dt = pytz.UTC.localize(fields.Datetime.from_string(convert_date)).astimezone(user_tz)
            dt = ustr(dt).split('+')[0]
            dt = datetime.strptime(str(dt), DEFAULT_SERVER_DATETIME_FORMAT).date()
        return dt

    @api.multi
    def get_from(self, product_categ_ids=[]):
        from_str = """
            stock_move_line sml
            inner join stock_move sm on sml.move_id = sm.id
            inner join product_product pp on sml.product_id = pp.id
        """
            # inner join stock_picking_type spt on (sm.picking_type_id = spt.id or sm.picking_type_id is null)
            # inner join stock_warehouse sw on spt.warehouse_id = sw.id
        if product_categ_ids:
            from_str = """
                %s inner join product_template pt on (pt.id = pp.product_tmpl_id and pt.categ_id in (%s))
            """ % (from_str, ','.join(map(str,self.product_categ_ids.ids)))
        else:
            from_str = """
                %s inner join product_template pt on pt.id = pp.product_tmpl_id
            """ % (from_str)
        return from_str

    @api.multi
    def get_where(self, location_ids=[], product_ids=[], from_date=False, to_date=False, location="all"):
        warehouse_locations = locations = self.env['stock.location'].search([('company_id', '=', self.company_id.id)]).filtered(lambda l: l.get_warehouse() and l.get_warehouse().id == self.warehouse_id.id)

        if self.env.context.get('check_from_date'):
            to_date = to_date.strftime(DEFAULT_SERVER_DATE_FORMAT + ' ' + '00:00:01')
        else:
            to_date = to_date.strftime(DEFAULT_SERVER_DATE_FORMAT + ' ' + '23:23:59')
        where_str = """
        sml.qty_done > 0
        and sml.date < '%s'
        and sm.company_id = %d""" % (to_date, self.company_id.id)
        # and sm.company_id = %d
        # and sml.location_id in %s or sml.location_dest_id in %s""" % (to_date, self.company_id.id,tuple(warehouse_locations.ids), tuple(warehouse_locations.ids))

        # if self.warehouse_id:
        #     where_str = """%s
        #         and sw.id = %d
        #     """ % (where_str, self.warehouse_id.id)

        # if self.warehouse_id.branch_id:
        #     where_str = """%s
        #         and sml.branch_id = %d
        #     """ % (where_str, self.warehouse_id.branch_id.id)
        # else:
        #     where_str = """%s
        #         and sml.branch_id is null
        #     """ % (where_str)

        if location == "all" and warehouse_locations:
            where_str = """%s
                and (sml.location_id in %s or sml.location_dest_id in %s)
            """ % (where_str, tuple(warehouse_locations.ids), tuple(warehouse_locations.ids))

        if location == "source" and warehouse_locations:
            where_str = """%s
                and sml.location_id in %s
            """ % (where_str, tuple(warehouse_locations.ids))

        if location == "dest" and warehouse_locations:
            where_str = """%s
                and sml.location_dest_id in %s
            """ % (where_str, tuple(warehouse_locations.ids))

        if self.available_in_pos:
            where_str = """%s
                and pt.available_in_pos = %s
            """ % (where_str, self.available_in_pos)

        if from_date:
            from_date = from_date.strftime(DEFAULT_SERVER_DATE_FORMAT + ' ' + '00:00:01')
            where_str = """%s
                and sml.date >= '%s'
            """ % (where_str, from_date)

        if location_ids:
            location_ids_str = ','.join(map(str,location_ids.ids))
            where_str = """%s
                            and (sml.location_id in (%s) or sml.location_dest_id in (%s))
                        """ % (where_str, location_ids_str, location_ids_str)

        if product_ids:
            where_str = """%s
                            and sml.product_id in (%s)
                        """ % (where_str, ','.join(map(str,product_ids.ids)))

        return where_str


    @api.multi
    def get_stock_move_line(self, location_ids=[], product_ids=[], product_categ_ids=[], from_date=False, to_date=False, location="all"):
        cr = self._cr
        report_query = """select
                            sml.id
                        from
                            %s
                        where
                            %s""" % (self.get_from(product_categ_ids=product_categ_ids),
                                     self.get_where(location_ids=location_ids, product_ids=product_ids,
                                                    from_date=from_date, to_date=to_date, location=location))
        cr.execute(report_query)
        return cr.fetchall()

    @api.multi
    def get_products(self):
        product_list = {}
        received_qty = 0.0
        delivered_qty = 0.0
        internal_transfer = 0.0
        adjustment = 0.0

        stock_move_line_ids = self.get_stock_move_line(location_ids=self.location_ids, product_ids=self.product_ids, product_categ_ids=self.product_categ_ids, from_date=self.from_date, to_date=self.to_date, location="all")
        move_line_ids = self.env['stock.move.line'].sudo().browse([i[0] for i in list(set(stock_move_line_ids))])

        # move_line_ids = move_line_ids.filtered(lambda l: (l.location_id.get_warehouse() and l.location_id.get_warehouse().id == self.warehouse_id.id) or (l.location_dest_id.get_warehouse() and l.location_dest_id.get_warehouse().id == self.warehouse_id.id))
        for stock_move_line in move_line_ids:
            move_uom_id = stock_move_line.product_uom_id
            product_uom_id = stock_move_line.product_id.uom_id
            from_location_warehouse = stock_move_line.location_id.get_warehouse()
            to_location_warehouse = stock_move_line.location_dest_id.get_warehouse()
            if not stock_move_line.product_id.id in product_list:
                product_list[stock_move_line.product_id.id] = {
                    'product': stock_move_line.product_id.name,
                    'product_id': stock_move_line.product_id.id,
                    'product_code': stock_move_line.product_id.default_code,
                    'initial_qty': 0.0,
                    'received_qty': 0.0,
                    'delivered_qty': 0.0,
                    'internal_transfer': 0.0,
                    'adjustment': 0.0,
                    'uom_id': stock_move_line.product_id.uom_id.name,
                    'product_uom_id': stock_move_line.product_id.uom_id.id,
                }
            if stock_move_line.location_id.usage in ['supplier','production']:
                product_list[stock_move_line.product_id.id]['received_qty'] += round(move_uom_id._compute_quantity(stock_move_line.qty_done, product_uom_id), 2)
            elif stock_move_line.location_dest_id.usage in ['supplier','production']:
                product_list[stock_move_line.product_id.id]['received_qty'] -= round(move_uom_id._compute_quantity(stock_move_line.qty_done, product_uom_id), 2)
            elif stock_move_line.location_dest_id.usage == 'customer':
                product_list[stock_move_line.product_id.id]['delivered_qty'] += round(move_uom_id._compute_quantity(stock_move_line.qty_done, product_uom_id), 2)
            elif stock_move_line.location_id.usage == 'customer':
                product_list[stock_move_line.product_id.id]['delivered_qty'] -= round(move_uom_id._compute_quantity(stock_move_line.qty_done, product_uom_id), 2)
            elif stock_move_line.location_id.usage == 'inventory':
                product_list[stock_move_line.product_id.id]['adjustment'] += round(move_uom_id._compute_quantity(stock_move_line.qty_done, product_uom_id), 2)
            elif stock_move_line.location_dest_id.usage == 'inventory':
                product_list[stock_move_line.product_id.id]['adjustment'] -= round(move_uom_id._compute_quantity(stock_move_line.qty_done, product_uom_id), 2)
            # elif stock_move_line.move_id.picking_id.picking_type_id.code == 'internal' and stock_move_line.move_id.location_id == stock_move_line.location_dest_id:
            elif stock_move_line.move_id.picking_id.picking_type_id.code == 'internal' and (to_location_warehouse and to_location_warehouse.id == self.warehouse_id.id) and to_location_warehouse != from_location_warehouse:
                product_list[stock_move_line.product_id.id]['internal_transfer'] += round(move_uom_id._compute_quantity(stock_move_line.qty_done, product_uom_id), 2)
            # elif stock_move_line.move_id.picking_id.picking_type_id.code == 'internal' and stock_move_line.move_id.location_id == stock_move_line.location_id:
            elif stock_move_line.move_id.picking_id.picking_type_id.code == 'internal' and (from_location_warehouse and from_location_warehouse.id == self.warehouse_id.id) and to_location_warehouse != from_location_warehouse:
                product_list[stock_move_line.product_id.id]['internal_transfer'] -= round(move_uom_id._compute_quantity(stock_move_line.qty_done, product_uom_id), 2)

        stock_move_line_ids = self.with_context({'check_from_date': True}).get_stock_move_line(location_ids=self.location_ids, product_ids=self.product_ids, product_categ_ids=self.product_categ_ids, from_date=False, to_date=self.from_date, location="dest")
        move_line_ids = self.env['stock.move.line'].sudo().browse([i[0] for i in list(set(stock_move_line_ids))])
        # move_line_ids_dest = move_line_ids.filtered(lambda l: (l.location_dest_id.get_warehouse() and l.location_dest_id.get_warehouse().id == self.warehouse_id.id))
        move_line_ids_dest = move_line_ids
        for stock_move_line in move_line_ids_dest:
            move_uom_id = stock_move_line.product_uom_id
            product_uom_id = stock_move_line.product_id.uom_id
            if stock_move_line.product_id.id in product_list:
                product_list[stock_move_line.product_id.id]['initial_qty'] += round(move_uom_id._compute_quantity(stock_move_line.qty_done, product_uom_id), 2)

        stock_move_line_ids = self.with_context({'check_from_date': True}).get_stock_move_line(location_ids=self.location_ids, product_ids=self.product_ids, product_categ_ids=self.product_categ_ids, from_date=False, to_date=self.from_date, location="source")
        move_line_ids = self.env['stock.move.line'].sudo().browse([i[0] for i in list(set(stock_move_line_ids))])
        # move_line_ids_source = move_line_ids.filtered(lambda l: (l.location_id.get_warehouse() and l.location_id.get_warehouse().id == self.warehouse_id.id))
        move_line_ids_source = move_line_ids
        for stock_move_line in move_line_ids_source:
            move_uom_id = stock_move_line.product_uom_id
            product_uom_id = stock_move_line.product_id.uom_id
            if stock_move_line.product_id.id in product_list:
                product_list[stock_move_line.product_id.id]['initial_qty'] -= round(move_uom_id._compute_quantity(stock_move_line.qty_done, product_uom_id), 2)

        for key in list(product_list.keys()):
            product_list[key]['balance_qty'] = round(product_list[key]['initial_qty'] + product_list[key]['received_qty'] - product_list[key]['delivered_qty'] + product_list[key]['internal_transfer'] + product_list[key]['adjustment'], 2)
        return product_list

    @api.multi
    def print_excel(self):
        header_content_style = xlwt.easyxf("font: name Times New Roman size 40 px , bold 1, height 280;align: vert centre, horiz centre")
        sub_header_style = xlwt.easyxf("font: name Times New Roman size 10 px, bold 1;align:horiz right")
        sub_header_style1 = xlwt.easyxf("font: name Times New Roman size 10 px, bold 1;align:horiz left")
        sub_header_style2 = xlwt.easyxf("font: name Times New Roman size 10 px, bold 1;align:horiz center")
        sub_header_content_style = xlwt.easyxf("font: name Times New Roman size 10 px;align:horiz right")
        sub_header_content_style1 = xlwt.easyxf("font: name Times New Roman size 10 px;align:horiz left")
        sub_header_content_style2 = xlwt.easyxf("font: name Times New Roman size 10 px;align:horiz center")
        line_content_style = xlwt.easyxf("font: name Times New Roman;")

        fp = BytesIO()
        wb = xlwt.Workbook()
        ws = wb.add_sheet('Inventory Movement')

        ws.col(0).width = 256*25
        ws.col(1).width = 256*20
        ws.col(2).width = 256*13
        ws.col(3).width = 256*16
        ws.col(4).width = 256*16
        ws.col(5).width = 256*19
        ws.col(6).width = 256*15
        ws.col(7).width = 256*15

        ws.write_merge(0, 3, 0, 7, "Inventory Movement", header_content_style)
        ws.write(5, 0, "From Date", sub_header_style2)
        ws.write(6, 0, str(self.get_date_as_per_user_timezone(self.from_date)), sub_header_content_style2)
        ws.write(5, 1, "To Date", sub_header_style2)
        ws.write(6, 1, str(self.get_date_as_per_user_timezone(self.to_date)), sub_header_content_style2)

        ws.write_merge(5, 5, 2, 3, "Warehouse", sub_header_style2)
        ws.write_merge(6, 6, 2, 3, self.warehouse_id.name, sub_header_content_style2)

        if self.filter_by == "product":
            ws.write_merge(5, 5, 4, 5, "Products", sub_header_style2)
            ws.write_merge(6, 6, 4, 5, ', '.join(self.product_ids.mapped('name')), sub_header_content_style2)
        else:
            ws.write_merge(5, 5, 4, 5, "Product Categories", sub_header_style2)
            ws.write_merge(6, 6, 4, 5, ', '.join(self.product_categ_ids.mapped('display_name')), sub_header_content_style2)

        ws.write_merge(5, 5, 6, 7, "Available in POS", sub_header_style2)
        ws.write_merge(6, 6, 6, 7, 'Yes' if self.available_in_pos else 'No', sub_header_content_style2)

        # ws.write_merge(5, 5, 4, 5, "Locations", sub_header_style2)
        # ws.write_merge(6, 6, 4, 5, ', '.join(self.location_ids.mapped('display_name')), sub_header_content_style2)

        ws.write_merge(9, 10, 0, 0, "Product", sub_header_style1)
        ws.write_merge(9, 10, 1, 1, "Description", sub_header_style1)
        ws.write_merge(9, 10, 2, 2, "UOM", sub_header_style1)
        ws.write_merge(9, 10, 3, 3, "Open Balance", sub_header_style)
        ws.write_merge(9, 10, 4, 4, "Sales", sub_header_style)
        ws.write_merge(9, 10, 5, 5, "Transfer In", sub_header_style)
        ws.write_merge(9, 10, 6, 6, "Transfer Out", sub_header_style)
        ws.write_merge(9, 10, 7, 7, "Adjustment", sub_header_style)
        ws.write_merge(9, 10, 8, 8, "Balance", sub_header_style)

        row = 11
        product_list = self.get_products()
        total_dict = {
            'initial_qty': 0.0,
            'delivered_qty': 0.0,
            'received_qty': 0.0,
            'internal_transfer': 0.0,
            'adjustment': 0.0,
            'balance_qty': 0.0,
        }
        for key in list(product_list.keys()):
            ws.write(row, 0, product_list[key]['product'], sub_header_content_style1)
            ws.write(row, 1, product_list[key]['product_code'] or '', sub_header_content_style1)
            ws.write(row, 2, product_list[key]['uom_id'], sub_header_content_style1)
            ws.write(row, 3, str(product_list[key]['initial_qty']), sub_header_content_style)
            ws.write(row, 4, str(product_list[key]['delivered_qty']), sub_header_content_style)
            ws.write(row, 5, str(product_list[key]['received_qty']), sub_header_content_style)
            ws.write(row, 6, str(product_list[key]['internal_transfer']), sub_header_content_style)
            ws.write(row, 7, str(product_list[key]['adjustment']), sub_header_content_style)
            ws.write(row, 8, str(product_list[key]['balance_qty']), sub_header_content_style)
            total_dict.update({
                'initial_qty': total_dict.get('initial_qty') + product_list[key]['initial_qty'],
                'delivered_qty': total_dict.get('delivered_qty') + product_list[key]['delivered_qty'],
                'received_qty': total_dict.get('received_qty') + product_list[key]['received_qty'],
                'internal_transfer': total_dict.get('internal_transfer') + product_list[key]['internal_transfer'],
                'adjustment': total_dict.get('adjustment') + product_list[key]['adjustment'],
                'balance_qty': total_dict.get('balance_qty') + product_list[key]['balance_qty'],
            })
            row += 1
        ws.write(row, 2, 'Total', sub_header_style)
        ws.write(row, 3, str(total_dict.get('initial_qty')), sub_header_style)
        ws.write(row, 4, str(total_dict.get('delivered_qty')), sub_header_style)
        ws.write(row, 5, str(total_dict.get('received_qty')), sub_header_style)
        ws.write(row, 6, str(total_dict.get('internal_transfer')), sub_header_style)
        ws.write(row, 7, str(total_dict.get('adjustment')), sub_header_style)
        ws.write(row, 8, str(total_dict.get('balance_qty')), sub_header_style)
        row += 1

        wb.save(fp)
        output = base64.encodestring(fp.getvalue())
        config_ids = self.env['ir.config_parameter'].sudo().search([('key', '=', 'web.base.url')])
        attachment_id = self.env['ir.attachment'].create({
            'name': 'Stock Inventory Analysis.xls',
            'datas': output,
            'datas_fname': 'Inventory Movement.xls',
            'res_model': 'stock.inventory.report',
            'res_id': self.id,
            'type': 'binary',
        })
        if attachment_id and len(config_ids):
            return {
                'name': 'Inventory Movement',
                'type': 'ir.actions.act_url',
                'url': '%s/web/content/%s?download=true' % (config_ids[0].value, attachment_id.id),
                'target': '_new',
            }
        self.write({'name': output, 'data':'Inventory Movement.xls'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.inventory.report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    @api.multi
    def generate_pdf_report(self):
        ctx = dict(self._context)
        product_list = self.get_products()
        ctx.update({'product_list' : product_list})
        report_action_ref = self.env.ref('sync_stock_inventory_report.action_report_stock_inventory')
        return report_action_ref.with_context(ctx).report_action(self)

    @api.multi
    def get_product_categ_name(self):
        names = ''
        if self.filter_by == "product":
            names = ', '.join(self.product_ids.mapped('name'))
        else:
            names = ', '.join(self.product_categ_ids.mapped('display_name'))
        if not names:
            names = 'All'
        return names

    @api.multi
    def get_locations_name(self):
        return ', '.join(self.location_ids.mapped('display_name')) or 'All'

    @api.multi
    def print_pivot(self):
        movement_pivot_obj = self.env['inventory.movement.pivot'].sudo()
        movement_pivot_obj.search([]).unlink()
        product_list = self.get_products()
        for key in list(product_list.keys()):
            movement_pivot_obj.create({
                'product_id': product_list[key]['product_id'],
                'uom_id': product_list[key]['product_uom_id'],
                'initial_qty': product_list[key]['initial_qty'],
                'delivered_qty': product_list[key]['delivered_qty'],
                'received_qty': product_list[key]['received_qty'],
                'internal_transfer': product_list[key]['internal_transfer'],
                'adjustment': product_list[key]['adjustment'],
                'balance_qty': product_list[key]['balance_qty']
            })
        return {
            'name': 'Inventory Movement',
            'type': 'ir.actions.act_window',
            'view_type': 'pivot',
            'view_mode': 'pivot,graph',
            'context': {},
            'res_model': 'inventory.movement.pivot',
        }
