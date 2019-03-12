# -*- coding: utf-8 -*-
# Part of Browseinfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date, timedelta
from odoo.exceptions import UserError
import datetime
import io
import base64
try:
    import xlwt
except ImportError:
    xlwt = None


class inventory_report_wizard(models.TransientModel):
    _name = "inventory.report.wizard"

    start_date = fields.Date(string="Start Date",required = True)
    end_date = fields.Date(string="End Date",required = True)
    warehouse_id = fields.Many2one('stock.warehouse',string="Warehouse",required = True)

    transfer_in_out = fields.Selection([('incoming','Incoming'),('outgoing','Outgoing')],string="Transfer Type",default='in',required = True)

    def print_pdf(self):

        return self.env.ref('bi_inventory_pos_report.inventory_report_pdf').report_action(self)
    


    def get_report_data(self) :

        pivot_inventory_rec = self.env['inventory.pivot.report'].search([])

        pivot_inventory_rec.unlink()

        vals = []
        domain = [('state','=','done')]
        if self.start_date :
            domain.append(('scheduled_date','>=',self.start_date))
        if self.end_date :

            domain.append(('scheduled_date','<=',self.end_date))

        if self.warehouse_id :
            domain.append(('branch_id','=',self.warehouse_id.branch_id.id))
        # if self.transfer_in_out:
        #     domain.append(('picking_type_id.code','=',self.transfer_in_out))
        stock_picking_rec = self.env['stock.picking'].search(domain)

      

        for res in stock_picking_rec :
            for line in res.move_ids_without_package :
                quantity = 0
                product_list = []
                for line in res.move_ids_without_package :

                  if line.picking_id.picking_type_id.code == 'internal':
                    if self.transfer_in_out == 'incoming' :
                        branch = res.location_id.branch_id.id

                        warehouse_name = self.env['stock.warehouse'].search([('branch_id','=',branch)])

                        if line.location_id.usage == 'inventory'  and line.location_dest_id.usage == 'internal':
                            quantity = quantity + line.product_uom_qty

                    if self.transfer_in_out == 'outgoing' :
                        branch = res.location_dest_id.branch_id.id

                        warehouse_name = self.env['stock.warehouse'].search([('branch_id','=',branch)])
                        if line.location_id.usage == 'internal'  and line.location_dest_id.usage == 'inventory':
                            quantity = quantity + line.product_uom_qty


                    a = self.env['inventory.pivot.report'].create({
                            'warehouse_id' : warehouse_name.id,
                           'source_doc' : res.origin,
                           'transfer_no' : res.name,
                           'date' : res.scheduled_date,
                           'product_id' : line.product_id.id,
                           'description': line.product_id.name,
                           'quantity' : line.product_uom_qty,
                           'unit' : line.product_uom.id,
                            'cost' : line.product_id.standard_price,
                            'total_cost' : line.product_id.standard_price * line.product_uom_qty
                })
                

        return vals




    def print_pivot(self):

        self.get_report_data()

        return {
            'name': 'Items Transfer',
            'type': 'ir.actions.act_window',
            'view_type': 'pivot',

            'view_mode': 'pivot,graph',
            'context': {},
            'res_model': 'inventory.pivot.report',
               
        }

    def get_lines(self):
      vals = []
      domain = [('state','=','done')]
      if self.start_date :
        domain.append(('scheduled_date','>=',self.start_date))
      if self.end_date :

        domain.append(('scheduled_date','<=',self.end_date))

      if self.warehouse_id :
        domain.append(('branch_id','=',self.warehouse_id.branch_id.id))

      # if self.transfer_in_out:
      #   domain.append(('picking_type_id.code','=',self.transfer_in_out))
      stock_picking_rec = self.env['stock.picking'].search(domain)

      
      for res in stock_picking_rec :
        for line in res.move_ids_without_package :
            quantity = 0
            product_list = []
            for line in res.move_ids_without_package :

              if line.picking_id.picking_type_id.code == 'internal':
                if self.transfer_in_out == 'incoming' :
                    branch = res.location_id.branch_id.id

                    warehouse_name = self.env['stock.warehouse'].search([('branch_id','=',branch)]).name

                    if line.location_id.usage == 'inventory'  and line.location_dest_id.usage == 'internal':
                        quantity = quantity + line.product_uom_qty

                if self.transfer_in_out == 'outgoing' :
                    branch = res.location_dest_id.branch_id.id

                    warehouse_name = self.env['stock.warehouse'].search([('branch_id','=',branch)]).name
                    if line.location_id.usage == 'internal'  and line.location_dest_id.usage == 'inventory':
                        quantity = quantity + line.product_uom_qty



                vals.append({'warehouse_name' : warehouse_name,
                               'source' : res.origin,
                               'transfer' : res.name,
                               'date' : res.scheduled_date,
                               'product' : line.product_id.name,
                               'description': line.product_id.name,
                               'quantity' : line.product_uom_qty,
                               'unit' : line.product_uom.name,
                               'cost' : line.product_id.standard_price,
                               'total_cost' : line.product_id.standard_price * line.product_uom_qty




                    })


      return vals


    def print_xls(self):
        badBG = xlwt.Pattern()
        badBG.SOLID_PATTERN = 0x34
        badBG.NO_PATTERN = 0x34
        badBG.pattern_fore_colour = 0x34
        badBG.pattern_back_colour = 0x34

        





        filename = 'Inventory Data.xls'
        workbook = xlwt.Workbook()
        stylePC = xlwt.XFStyle()
        stylePC.Pattern = badBG
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        fontP = xlwt.Font()
        fontP.bold = True
        fontP.height = 200
        stylePC.font = fontP
        stylePC.num_format_str = '@'
        stylePC.alignment = alignment
        style_title = xlwt.easyxf("font:height 200;pattern: pattern solid, pattern_fore_colour gray25;font: name Liberation Sans, bold on,color black; align: horiz center")
        style_table_header = xlwt.easyxf("font:height 200; font: name Liberation Sans, bold on,color black; align: horiz center")
        style = xlwt.easyxf("font:height 200; font: name Liberation Sans,color black;")
        worksheet = workbook.add_sheet('Sheet 1')
        title = "Items Transfer"
        worksheet.write(1, 1,'Start Date:')
        worksheet.write(1, 2,str(self.start_date.strftime("%d-%m-%Y")))
        worksheet.write(1, 9,'End Date:')
        worksheet.write(1, 10,str(self.end_date.strftime("%d-%m-%Y")))
        
        worksheet.write(0, 1,self.warehouse_id.name)
        if self.transfer_in_out == 'incoming':

            worksheet.write(0, 4,'Incoming Transfer')

        if self.transfer_in_out == 'outgoing':

            worksheet.write(0, 4,'Outgoing Transfer')


        worksheet.write_merge(2, 2, 1, 10, title, style=style_title)
        
        worksheet.write(3, 1, 'Warehouse', style_title)
        worksheet.write(3, 2, 'Source Document', style_title)
        worksheet.write(3, 3, 'Transfer No', style_title)
        worksheet.write(3, 4, 'Date', style_title)
        worksheet.write(3, 5, 'Product', style_title)
        worksheet.write(3, 6, 'Description', style_title)
        worksheet.write(3, 7, 'Qty', style_title)
        worksheet.write(3, 8, 'Unit', style_title)
        worksheet.write(3, 9, 'Unit Cost', style_title)
        worksheet.write(3, 10, 'Total Cost', style_title)
        
        
        lines = self.get_lines()
        row = 4
        clos = 0
        total = 0
        for line in lines :
            worksheet.write(row, 1,line['warehouse_name'])
            worksheet.write(row, 2,line['source'])
            worksheet.write(row, 3,line['transfer'])
            worksheet.write(row, 4,str(line['date']))
            worksheet.write(row, 5,line['product'])
            worksheet.write(row, 6,line['description'])
            worksheet.write(row, 7,line['quantity'])
            worksheet.write(row, 8,line['unit'])
            worksheet.write(row, 9,line['cost'])
            worksheet.write(row, 10,line['total_cost'])
            total = total + line['quantity']
            
            row = row+1
        worksheet.write(row + 1, 6,'Total = ')
        worksheet.write(row + 1, 7,total)
        fp = io.BytesIO()
        workbook.save(fp)
        
        export_id = self.env['inventory.report.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        res = {
                        'view_mode': 'form',
                        'res_id': export_id.id,
                        'res_model': 'inventory.report.excel',
                        'view_type': 'form',
                        'type': 'ir.actions.act_window',
                        'target':'new'
                }
        return res


class inventory_xls_report(models.TransientModel):
    _name = "inventory.report.excel"
    
    
    excel_file = fields.Binary('Excel Report Inventory')
    file_name = fields.Char('Excel File', size=64)

