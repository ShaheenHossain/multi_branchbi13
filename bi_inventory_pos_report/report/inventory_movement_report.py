# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import models, api






class inventory_pdf_movement_report(models.AbstractModel):
    _name = 'report.bi_inventory_pos_report.inventory_movement_pdf_template'
    
    @api.multi
    def _get_report_values(self, docids, data=None):
        data = data if data is not None else {}
        docs = self.env['inventory.movement.wizard'].browse(docids)
        data  = { 'start_date': docs.start_date, 'end_date': docs.end_date,
                'warehouse_id':docs.warehouse_id
                }
        
        return {
                   'doc_model': 'inventory.movement.wizard',
                   'data' : data,

                   
                   'get_lines':self._get_lines(data),
                   
                   }


    def _get_lines(self,data):

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


