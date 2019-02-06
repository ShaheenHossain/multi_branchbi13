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


class pos_report_wizard(models.TransientModel):
    _name = "pos.report.wizard"

    start_date = fields.Date(string="Start Date",required = True)
    end_date = fields.Date(string="End Date",required = True)
    warehouse_id = fields.Many2one('stock.warehouse',string="Warehouse",required = True)






    def print_pivot(self):
        data  = { 'start_date': self.start_date, 'end_date': self.end_date,
                'warehouse_id':self.warehouse_id
                }
        self.get_report_data(data)

        return {
            'name': 'Inventory Report',
            'type': 'ir.actions.act_window',
            'view_type': 'pivot',

            'view_mode': 'pivot',
            'context': {},
            'res_model': 'pos.pivot.report',
               
        }


    def get_report_data(self,data):

        
        pivot_rec = self.env['pos.pivot.report'].search([])

        pivot_rec.unlink()
        vals = []
        domain = [('order_id.state','in',['done','paid'])]
        if data['start_date'] :
            domain.append(('order_id.date_order','>=',data['start_date']))
        if data['end_date'] :

            domain.append(('order_id.date_order','<=',data['end_date']))

          # if data['branch_id'] :
          #   domain.append(('order_id.branch_id','=',data['branch_id'].id))
        pos_line_rec = self.env['pos.order.line'].search(domain)

      
        for line in pos_line_rec :
            warehouse = self.env['stock.warehouse'].search([('branch_id','=',line.order_id.branch_id.id)])
            if warehouse.id == data['warehouse_id'].id:
                self.env['pos.pivot.report'].create({'product_id' : line.product_id.id,
                        'description' : line.product_id.name,
                        'sale_qty' : line.qty,
                        'price': line.price_unit,
                        'discount' : line.discount,
                        'net_sales' : line.price_subtotal,
                        'vat' : line.tax_ids_after_fiscal_position.amount,
                        'total' : line.price_subtotal_incl
                        })


     
        return vals







    def print_pdf(self):

        return self.env.ref('bi_inventory_pos_report.pos_report_pdf').report_action(self)


    def get_payments(self,data):
      domain_a = [('state','in',['done','paid'])]
      if data['start_date'] :
        domain_a.append(('date_order','>=',data['start_date']))
      if data['end_date'] :

        domain_a.append(('date_order','<=',data['end_date']))

      # if data['branch_id'] :
      #   domain_a.append(('branch_id','=',data['branch_id'].id))
      pos_order = self.env['pos.order'].search(domain_a)

      payment_dict = {}
      for order in pos_order:
        warehouse = self.env['stock.warehouse'].search([('branch_id','=',order.branch_id.id)])
        if warehouse.id == data['warehouse_id'].id:
          for line in order.statement_ids :
            if line.journal_id.name in payment_dict :
              payment_dict[line.journal_id.name] = payment_dict[line.journal_id.name] + (line.amount)

            else : 
              payment_dict[line.journal_id.name] =  (line.amount)

      vals = []     
      for key in payment_dict: 
        
        vals.append({'name':key,'amount':payment_dict[key]})
      return vals






    def get_lines(self,data):

      vals = []
      domain = [('order_id.state','in',['done','paid'])]
      if data['start_date'] :
        domain.append(('order_id.date_order','>=',data['start_date']))
      if data['end_date'] :

        domain.append(('order_id.date_order','<=',data['end_date']))

      # if data['branch_id'] :
      #   domain.append(('order_id.branch_id','=',data['branch_id'].id))
      pos_line_rec = self.env['pos.order.line'].search(domain)

      
      for line in pos_line_rec :
        warehouse = self.env['stock.warehouse'].search([('branch_id','=',line.order_id.branch_id.id)])
        if warehouse.id == data['warehouse_id'].id:
          vals.append({'name' : line.product_id.name,
                      'description' : line.product_id.name,
                      'sale_qty' : line.qty,
                      'price': line.price_unit,
                      'discount' : line.discount,
                      'net_sales' : line.price_subtotal,
                      'vat' : line.tax_ids_after_fiscal_position.amount,
                      'total' : line.price_subtotal_incl
                      })


     
      return vals



    def print_xls(self):
        badBG = xlwt.Pattern()
        badBG.SOLID_PATTERN = 0x34
        badBG.NO_PATTERN = 0x34
        badBG.pattern_fore_colour = 0x34
        badBG.pattern_back_colour = 0x34

        





        filename = 'POS Data.xls'
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
        title = "Daily Close Report"
        worksheet.write(0, 3,'Start Date:')
        worksheet.write(0, 4,str(self.start_date))
        worksheet.write(0, 1,self.warehouse_id.name)
        worksheet.write(0, 7,'End Date:')
        worksheet.write(0, 8,str(self.end_date))
        
        worksheet.write_merge(1, 1, 1, 8, title, style=style_title)
        
        worksheet.write(2, 1, 'Product', style_title)
        worksheet.write(2, 2, 'Description', style_title)
        worksheet.write(2, 3, 'Sales Qty', style_title)
        worksheet.write(2, 4, 'Price', style_title)
        worksheet.write(2, 5, 'Discount', style_title)
        worksheet.write(2, 6, 'Net Sales Amount', style_title)
        worksheet.write(2, 7, 'VAT', style_title)
        worksheet.write(2, 8, 'Total', style_title)

        data  = { 'start_date': self.start_date, 'end_date': self.end_date,
                'warehouse_id':self.warehouse_id
                }
        
        lines = self.get_lines(data)
        row = 3
        clos = 0
        total_sl = 0
        total_prs = 0
        total_ds = 0
        total_ns = 0
        total_vat = 0
        total_t = 0
        for line in lines :
            worksheet.write(row, 1,line['name'])
            worksheet.write(row, 2,line['description'])
            worksheet.write(row, 3,line['sale_qty'])
            worksheet.write(row, 4,line['price'])
            worksheet.write(row, 5,line['discount'])
            worksheet.write(row, 6,line['net_sales'])
            worksheet.write(row, 7,line['vat'])
            worksheet.write(row, 8,line['total'])
            

            total_sl = total_sl + line['sale_qty']
            total_prs = total_prs + line['price']
            total_ds = total_ds + line['discount']
            total_ns = total_ns + line['net_sales']
            total_vat = total_vat + line['vat']
            total_t = total_t + line['total']
            
            row = row+1
        worksheet.write(row + 1, 2,'Total = ')
        worksheet.write(row + 1, 3,total_sl)
        worksheet.write(row + 1, 4,total_prs)
        worksheet.write(row + 1, 5,total_ds)
        worksheet.write(row + 1, 6,total_ns)
        worksheet.write(row + 1, 7,total_vat)
        worksheet.write(row + 1, 8,total_t)
        row = row + 2
        payments = self.get_payments(data)
        row = row +1
        worksheet.write(row, 1, 'Name', style_title)
        worksheet.write(row, 2, 'Amount', style_title)
        
        row = row +1

        for pay in payments :
            worksheet.write(row, 1,pay['name'])
            worksheet.write(row, 2,pay['amount'])
            row = row +1
        
        fp = io.BytesIO()
        workbook.save(fp)
        
        export_id = self.env['pos.report.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        res = {
                        'view_mode': 'form',
                        'res_id': export_id.id,
                        'res_model': 'pos.report.excel',
                        'view_type': 'form',
                        'type': 'ir.actions.act_window',
                        'target':'new'
                }
        return res


class pos_xls_report(models.TransientModel):
    _name = "pos.report.excel"
    
    
    excel_file = fields.Binary('Excel Daily Close Report')
    file_name = fields.Char('Excel File', size=64)


    
