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


class inventory_movemrnt_wizard(models.TransientModel):
    _name = "inventory.movement.wizard"

    start_date = fields.Date(string="Start Date",required = True)
    end_date = fields.Date(string="End Date",required = True)
    warehouse_id = fields.Many2one('stock.warehouse',string="Warehouse",required = True)


    def print_pdf(self):

        return self.env.ref('bi_inventory_pos_report.inventory_movement_report_pdf').report_action(self)
    





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
            'res_model': 'inventory.movement.report',
               
        }




    def get_report_data(self,data) :


      pivot_inventory_rec = self.env['inventory.movement.report'].search([])

      pivot_inventory_rec.unlink()

      vals = []
      product_list = []
      domain_1 = [('state','=','done')]
      if data['start_date'] :
        domain_1.append(('date_expected','>=',data['start_date']))
      if data['end_date'] :

        domain_1.append(('date_expected','<=',data['end_date']))

      if data['warehouse_id'] :
        domain_1.append(('warehouse_id','=',data['warehouse_id'].id))

      #domain_1.append(('product_id','in',product_list))

      move_line_rec = self.env['stock.move'].search(domain_1)

      

      print ("aaaaaaaaaaaaaaaaaaaaa",move_line_rec)

      for pro in move_line_rec :
        if pro.product_id.id not in product_list :
          product_list.append(pro.product_id.id)



      for pro_id in product_list :
        pro_obj = self.env['product.product'].browse(pro_id)
        name = pro_obj.name
        
        move_line_opening = self.env['stock.move'].search([
                                                            
                                                            ('product_id','=',pro_id),
                                                            ('warehouse_id','=',data['warehouse_id'].id)

                                                            ])

        incoming = 0
        outgoing = 0
        for line in move_line_opening :
          date_1 = line.date_expected.date()
          print ("11111111111111111111111",date_1,'222222222222222222222222222',data['start_date'])
          if date_1 == data['start_date'] :
            if line.picking_id.picking_type_id.code == 'outgoing':
              outgoing = outgoing + line.product_uom_qty

            if line.picking_id.picking_type_id.code == 'incoming':
              incoming = incoming + line.product_uom_qty


        opening_qty = incoming - outgoing







        move_line = self.env['stock.move'].search([
                                                  ('date_expected','>=',data['start_date']),
                                                  ('date_expected','<=',data['end_date']),
                                                   ('warehouse_id','=',data['warehouse_id'].id),
                                                   ('product_id','=',pro_id)
                                                    ])

        inventory_adj_line = self.env['stock.inventory.line'].search([
                                                  ('inventory_id.date','>=',data['start_date']),
                                                  ('inventory_id.date','<=',data['end_date']),
                                                  #('inventory_id.branch_id','=',data['branch_id'].id),
                                                  ('product_id','=',pro_id),
                                                  ('inventory_id.state','=','done')
          ])
        
        adjestment= 0
        product_list = []
        for line in inventory_adj_line :
          warehouse = self.env['stock.warehouse'].search([('branch_id','=',line.inventory_id.branch_id.id)])
          if warehouse.id == data['warehouse_id'].id :
            print ("sssssssssssssssssssssssssssssssssssss",line.inventory_id.name)
            product_list.append(line.id)

          

        print ("llllllllllllllllllllllllllllllllllllllllllllll",product_list)
        max_id = 0
        for i in product_list :
          if i > max_id :
            max_id = i

        if max_id > 0 :
          print ("name======================================",self.env['stock.inventory.line'].browse(max_id).inventory_id.name)
          adjestment = self.env['stock.inventory.line'].browse(max_id).product_qty

        
        
        
        

        recived_qty = 0
        sale_qty = 0
        for line in move_line :
          if line.picking_id.picking_type_id.code == 'outgoing':
            sale_qty = sale_qty + line.product_uom_qty

          if line.picking_id.picking_type_id.code == 'incoming':
            recived_qty = sale_qty + line.product_uom_qty


        self.env['inventory.movement.report'].create({'product_id':pro_obj.id,
                    'description' : name,
                    'opening' : opening_qty,
                    'recieved' : recived_qty,
                    'sale_qty' : sale_qty,
                    'adjestment' : adjestment,
                    'balance' : opening_qty + recived_qty - sale_qty + adjestment





                    })


      return 


    def get_lines(self,data):

      vals = []
      product_list = []
      domain_1 = [('state','=','done')]
      if data['start_date'] :
        domain_1.append(('date_expected','>=',data['start_date']))
      if data['end_date'] :

        domain_1.append(('date_expected','<=',data['end_date']))

      if data['warehouse_id'] :
        domain_1.append(('warehouse_id','=',data['warehouse_id'].id))

      #domain_1.append(('product_id','in',product_list))

      move_line_rec = self.env['stock.move'].search(domain_1)

      

      print ("aaaaaaaaaaaaaaaaaaaaa",move_line_rec)

      for pro in move_line_rec :
        if pro.product_id.id not in product_list :
          product_list.append(pro.product_id.id)



      for pro_id in product_list :
        pro_obj = self.env['product.product'].browse(pro_id)
        name = pro_obj.name
        
        move_line_opening = self.env['stock.move'].search([
                                                            
                                                            ('product_id','=',pro_id),
                                                            ('warehouse_id','=',data['warehouse_id'].id)

                                                            ])

        incoming = 0
        outgoing = 0
        for line in move_line_opening :
          date_1 = line.date_expected.date()
          print ("11111111111111111111111",date_1,'222222222222222222222222222',data['start_date'])
          if date_1 == data['start_date'] :
            if line.picking_id.picking_type_id.code == 'outgoing':
              outgoing = outgoing + line.product_uom_qty

            if line.picking_id.picking_type_id.code == 'incoming':
              incoming = incoming + line.product_uom_qty


        opening_qty = incoming - outgoing







        move_line = self.env['stock.move'].search([
                                                  ('date_expected','>=',data['start_date']),
                                                  ('date_expected','<=',data['end_date']),
                                                   ('warehouse_id','=',data['warehouse_id'].id),
                                                   ('product_id','=',pro_id)
                                                    ])

        inventory_adj_line = self.env['stock.inventory.line'].search([
                                                  ('inventory_id.date','>=',data['start_date']),
                                                  ('inventory_id.date','<=',data['end_date']),
                                                  #('inventory_id.branch_id','=',data['branch_id'].id),
                                                  ('product_id','=',pro_id),
                                                  ('inventory_id.state','=','done')
          ])
        
        adjestment= 0
        product_list = []
        for line in inventory_adj_line :
          warehouse = self.env['stock.warehouse'].search([('branch_id','=',line.inventory_id.branch_id.id)])
          if warehouse.id == data['warehouse_id'].id :
            print ("sssssssssssssssssssssssssssssssssssss",line.inventory_id.name)
            product_list.append(line.id)

          

        print ("llllllllllllllllllllllllllllllllllllllllllllll",product_list)
        max_id = 0
        for i in product_list :
          if i > max_id :
            max_id = i

        if max_id > 0 :
          print ("name======================================",self.env['stock.inventory.line'].browse(max_id).inventory_id.name)
          adjestment = self.env['stock.inventory.line'].browse(max_id).product_qty

        
        
        
        

        recived_qty = 0
        sale_qty = 0
        for line in move_line :
          if line.picking_id.picking_type_id.code == 'outgoing':
            sale_qty = sale_qty + line.product_uom_qty

          if line.picking_id.picking_type_id.code == 'incoming':
            recived_qty = sale_qty + line.product_uom_qty


        vals.append({'pro_name':name,
                    'description' : name,
                    'opening' : opening_qty,
                    'received' : recived_qty,
                    'sale_qty' : sale_qty,
                    'adjestment': adjestment,
                    'balance' : opening_qty + recived_qty - sale_qty + adjestment





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
        title = ""
        worksheet.write(0, 1,'Start Date:')
        worksheet.write(0, 2,str(self.start_date))
        worksheet.write(0, 6,'End Date:')
        worksheet.write(0, 7,str(self.end_date))
        
        worksheet.write_merge(1, 1, 1, 7, title, style=style_title)
        
        worksheet.write(2, 1, 'Product', style_title)
        worksheet.write(2, 2, 'Description', style_title)
        worksheet.write(2, 3, 'Opening Balance Qty', style_title)
        worksheet.write(2, 4, 'Received Qty', style_title)
        worksheet.write(2, 5, 'Sales Qty', style_title)
        worksheet.write(2, 6, 'Adjesment Qty', style_title)
        worksheet.write(2, 7, 'Balance', style_title)
        
        data  = { 'start_date': self.start_date, 'end_date': self.end_date,
                'warehouse_id':self.warehouse_id
                }
        lines = self.get_lines(data)
        row = 3
        clos = 0
        total_opn = 0
        total_rcv = 0
        total_sl = 0
        total_adj = 0
        total_bal = 0
        for line in lines :
            worksheet.write(row, 1,line['pro_name'])
            worksheet.write(row, 2,line['description'])
            worksheet.write(row, 3,line['opening'])
            worksheet.write(row, 4,line['received'])
            worksheet.write(row, 5,line['sale_qty'])
            worksheet.write(row, 6,line['adjestment'])
            worksheet.write(row, 7,line['balance'])
            
            total_opn = total_opn + line['opening']
            total_rcv = total_rcv + line['received']
            total_sl = total_sl + line['sale_qty']
            total_adj = total_adj + line['adjestment']
            total_bal = total_bal + line['balance']
            
            row = row+1

        worksheet.write(row + 1, 2,"Total = ")
        worksheet.write(row + 1, 3,total_opn)
        worksheet.write(row + 1, 4,total_rcv)
        worksheet.write(row + 1, 5,total_sl)
        worksheet.write(row + 1, 6,total_adj)
        worksheet.write(row + 1, 7,total_bal)
    
        fp = io.BytesIO()
        workbook.save(fp)
        
        export_id = self.env['inventory.movement.excel'].create({'excel_file': base64.encodestring(fp.getvalue()), 'file_name': filename})
        res = {
                        'view_mode': 'form',
                        'res_id': export_id.id,
                        'res_model': 'inventory.movement.excel',
                        'view_type': 'form',
                        'type': 'ir.actions.act_window',
                        'target':'new'
                }
        return res


class inventory_movement_xls_report(models.TransientModel):
    _name = "inventory.movement.excel"
    
    
    excel_file = fields.Binary('Excel Report Inventory')
    file_name = fields.Char('Excel File', size=64)

