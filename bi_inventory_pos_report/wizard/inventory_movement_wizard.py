from odoo import models, fields, api, _
from datetime import date, timedelta
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round




import datetime
import io
import base64
try:
    import xlwt
except ImportError:
    xlwt = None


class inventory_movemrnt_wizard(models.TransientModel):
    _name = "inventory.movement.wizard"
    _description = "Inventory Movement"

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
            'name': 'Inventory Movement',
            'type': 'ir.actions.act_window',
            'view_type': 'pivot',

            'view_mode': 'graph,pivot',
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
        #domain_1.append(('warehouse_id','=',data['warehouse_id'].id))
        domain_1.append(('picking_id.branch_id','=',data['warehouse_id'].branch_id.id))

      #domain_1.append(('product_id','in',product_list))

      move_line_rec = self.env['stock.move'].search(domain_1)

      

      

      for pro in move_line_rec :
        if pro.product_id.id not in product_list :
          product_list.append(pro.product_id.id)



      domain_2 = [('state','=','done')]
      if data['start_date'] :
        domain_2.append(('inventory_id.date','>=',data['start_date']))
      if data['end_date'] :

        domain_2.append(('inventory_id.date','<=',data['end_date']))

      if data['warehouse_id'] :
        domain_2.append(('inventory_id.branch_id','=',data['warehouse_id'].branch_id.id))

      

      new_move_line_rec = self.env['stock.move'].search(domain_2)


      for pro_id in new_move_line_rec :

        if pro_id.product_id.id not in product_list :
          product_list.append(pro_id.product_id.id)



      domain_p = [('order_id.state','in',['done','paid'])]
      if data['start_date'] :
        domain_p.append(('order_id.date_order','>=',data['start_date']))
      if data['end_date'] :

        domain_p.append(('order_id.date_order','<=',data['end_date']))

      if data['warehouse_id'] :
        
        domain_p.append(('order_id.branch_id','=',data['warehouse_id'].branch_id.id))



      
      pos_line_rec = self.env['pos.order.line'].search(domain_p)

      for p in pos_line_rec :
        if p.product_id.id not in product_list :
          product_list.append(p.product_id.id)



      domain_m = [('state','=','done')]
      
      if data['warehouse_id'] :
        domain_m.append(('branch_id','=',data['warehouse_id'].branch_id.id))

      manufacturing_orders_res = self.env['mrp.production'].search(domain_m)

      for res in manufacturing_orders_res :
        manu_products = []
        for product in res.finished_move_line_ids :
          manu_products.append(product.product_id.id)

        for pick in res.picking_ids:
          if pick.state == 'done' and pick.date_done.date() >= data['start_date'] and pick.date_done.date() <= data['end_date']:

            for line in pick.move_ids_without_package :
              if line.product_id.id in manu_products :
                if line.product_id.id not in product_list :
                  product_list.append(line.product_id.id)




      for pro_id in product_list :
        pro_obj = self.env['product.product'].browse(pro_id)
        name = pro_obj.name
        uom = pro_obj.uom_id.id
        
        opening = self._compute_quantities_product_quant_dic(False,data['start_date'],pro_obj,data)
        
        opening_qty = opening[pro_obj.id]['qty_available']

        if opening_qty < 0:
          opening_qty =0

        
        #bal = pro_obj._compute_quantities_dict(pro_obj._context.get('lot_id'), pro_obj._context.get('owner_id'), pro_obj._context.get('package_id'), data['end_date'])
        bal = self._compute_quantities_product_quant_dic(False,data['end_date'],pro_obj,data)
        
        
        bal_qty = bal[pro_obj.id]['qty_available']

        if bal_qty < 0 :
          bal_qty = 0

        move_line_opening = self.env['stock.move'].search([
                                                            ('state','=','done'),
                                                            ('product_id','=',pro_id),
                                                            ('warehouse_id','=',data['warehouse_id'].id)

                                                            ])
        
        incoming = 0
        outgoing = 0
        for line in move_line_opening :
          date_1 = line.date_expected.date()
          
          if date_1 == data['start_date'] :
            if line.picking_id.picking_type_id.code == 'outgoing':
              outgoing = outgoing + line.product_uom_qty

            if line.picking_id.picking_type_id.code == 'incoming':
              incoming = incoming + line.product_uom_qty









        move_line = self.env['stock.move'].search([
                                                  ('state','=','done'),
                                                  ('date_expected','>=',data['start_date']),
                                                  ('date_expected','<=',data['end_date']),
                                                   
                                                   ('product_id','=',pro_id),
                                                   ('picking_id.branch_id','=',data['warehouse_id'].branch_id.id)

                                                    ])

        inventory_adj_line = self.env['stock.inventory.line'].search([
                                                  ('inventory_id.date','>=',data['start_date']),
                                                  ('inventory_id.date','<=',data['end_date']),
                                                  ('inventory_id.branch_id','=',data['warehouse_id'].branch_id.id),
                                                  ('product_id','=',pro_id),
                                                  ('inventory_id.state','=','done')
          ])
        
        adjestment= 0
        product_list = []
        for line in inventory_adj_line :
          warehouse = self.env['stock.warehouse'].search([('branch_id','=',line.inventory_id.branch_id.id)])
          if warehouse.id == data['warehouse_id'].id :
            
            product_list.append(line.id)

          

        
        max_id = 0
        for i in product_list :
          if i > max_id :
            max_id = i

        if max_id > 0 :
          
          adjestment = self.env['stock.inventory.line'].browse(max_id).product_qty

        
        
        
        

        recived_qty = 0
        sale_qty = 0
        for line in move_line :
          if line.picking_id.picking_type_id.code == 'outgoing':
            sale_qty = sale_qty + line.product_uom_qty

          if line.picking_id.picking_type_id.code == 'incoming':
            recived_qty = recived_qty + line.product_uom_qty


          if line.picking_id.picking_type_id.code == 'internal':
            if line.location_id.usage == 'inventory'  and line.location_dest_id.usage == 'internal':
              recived_qty = recived_qty + line.product_uom_qty
          
          if line.location_id.usage == 'inventory'  :
            
            recived_qty = recived_qty + line.product_uom_qty


        
        # new_move_lines = self.env['stock.move'].search([
                                                  
        #                                           ('inventory_id.date','>=',data['start_date']),
        #                                           ('inventory_id.date','<=',data['end_date']),
        #                                           ('inventory_id.branch_id','=',data['warehouse_id'].branch_id.id),
        #                                           ('product_id','=',pro_id),
        #                                           ('inventory_id.state','=','done')
        #   ])
        
        
        # for line in new_move_lines :
          
        #   if line.location_id.usage == 'inventory'  and line.location_dest_id.usage == 'internal':
           
        #     recived_qty = recived_qty + line.product_uom_qty


       
        domain_man = [('state','=','done')]
      
        if data['warehouse_id'] :
          domain_man.append(('branch_id','=',data['warehouse_id'].branch_id.id))

        manufacturing_orders_res = self.env['mrp.production'].search(domain_man)

        for res in manufacturing_orders_res :
          

          for pick in res.picking_ids:
            if pick.state == 'done' and pick.date_done.date() >= data['start_date'] and pick.date_done.date() <= data['end_date']:

              for line in pick.move_ids_without_package :
                if line.product_id.id == pro_id :
                  recived_qty = recived_qty + line.product_uom_qty


        
            




      

        self.env['inventory.movement.report'].create({'product_id':pro_id,
                    'description' : name,
                    'opening' : opening_qty,
                    'recieved' : float(recived_qty),
                    'sale_qty' : sale_qty,
                    'adjestment': adjestment,
                    'balance' : bal_qty,
                    'id' : pro_id,
                    'uom' : uom,

                    })


      product_res = self.env['product.product'].search([('qty_available', '!=', 0),
                                                                ('type', '=', 'product'),

                                                                ])
        
      for pro in product_res :
        if pro.id not in product_list :
          if pro.create_date.date() <= data['start_date'] :

              opening = self._compute_quantities_product_quant_dic(False,data['start_date'],pro,data)
        
              opening_qty_n = opening[pro.id]['qty_available']


              bal = self._compute_quantities_product_quant_dic(False,data['end_date'],pro,data)
        
        
              bal_qty = bal[pro.id]['qty_available']

              self.env['inventory.movement.report'].create({'product_id':pro.id,
                    'description' : pro.name,
                    'opening' : opening_qty_n,
                    'recieved' : 0,
                    'sale_qty' : 0,
                    'adjestment': 0,
                    'balance' : bal_qty,
                    'id' : pro.id,
                    'uom' : pro.uom_id.id,

                    })

      return 



    def _compute_quantities_product_quant_dic(self,from_date,to_date,product_obj,data):
            
            loc_list = []
                
            domain_quant_loc, domain_move_in_loc, domain_move_out_loc = product_obj._get_domain_locations()
            branch__quant_domain = []
            if data['warehouse_id'] :
                ware_check_domain = [a.id for a in data['warehouse_id']]
                for i in ware_check_domain:
                  
                  loc_ids = self.env['stock.warehouse'].search([('id','=',i)])
                  locations = []
                  locations.append(loc_ids.view_location_id.id)
                  for i in loc_ids.view_location_id.child_ids :
                    locations.append(i.id)

                  
                 
                  loc_list.append(loc_ids.lot_stock_id.id)

                  
                  branch__quant_domain.append(('location_id','in',locations))
                #branch__quant_domain = [('location_id.branch_id','=',data['warehouse_id'].branch_id.id)]
            domain_quant = [('product_id', 'in', product_obj.ids)] + domain_quant_loc + branch__quant_domain
            #print ("dddddddddddddddddddddddddddddddddddddddddd",domain_quant)
            dates_in_the_past = False
            # only to_date as to_date will correspond to qty_available
            #to_date = fields.Datetime.to_datetime(to_date)
            
            if to_date and to_date < date.today():

                dates_in_the_past = True

            domain_move_in = [('product_id', 'in', product_obj.ids)] + domain_move_in_loc
            domain_move_out = [('product_id', 'in', product_obj.ids)] + domain_move_out_loc
            # if lot_id is not None:
            #     domain_quant += [('lot_id', '=', lot_id)]
            # if owner_id is not None:
            #     domain_quant += [('owner_id', '=', owner_id)]
            #     domain_move_in += [('restrict_partner_id', '=', owner_id)]
            #     domain_move_out += [('restrict_partner_id', '=', owner_id)]
            # if package_id is not None:
            #     domain_quant += [('package_id', '=', package_id)]
            if dates_in_the_past:
                domain_move_in_done = list(domain_move_in)
                domain_move_out_done = list(domain_move_out)
            if from_date:
                domain_move_in += [('date', '>=', from_date)]
                domain_move_out += [('date', '>=', from_date)]
            if to_date:
                domain_move_in += [('date', '<=', to_date)]
                domain_move_out += [('date', '<=', to_date)]

            Move = self.env['stock.move']
            Quant = self.env['stock.quant']
            domain_move_in_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_in
            domain_move_out_todo = [('state', 'in', ('waiting', 'confirmed', 'assigned', 'partially_available'))] + domain_move_out
            moves_in_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
            moves_out_res = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_todo, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
            quants_res = dict((item['product_id'][0], item['quantity']) for item in Quant.read_group(domain_quant, ['product_id', 'quantity'], ['product_id'], orderby='id'))
            #for item in Quant.search(domain_quant) :
                #print ("qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq",item)
            if dates_in_the_past:
                # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
                domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
                domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
                moves_in_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_in_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))
                moves_out_res_past = dict((item['product_id'][0], item['product_qty']) for item in Move.read_group(domain_move_out_done, ['product_id', 'product_qty'], ['product_id'], orderby='id'))

            res = dict()
            for product in product_obj.with_context(prefetch_fields=False):
                product_id = product.id
                rounding = product.uom_id.rounding
                res[product_id] = {}
                if dates_in_the_past:
                    qty_available = quants_res.get(product_id, 0.0) - moves_in_res_past.get(product_id, 0.0) + moves_out_res_past.get(product_id, 0.0)
                else:
                    qty_available = quants_res.get(product_id, 0.0)
                res[product_id]['qty_available'] = float_round(qty_available, precision_rounding=rounding)
                res[product_id]['incoming_qty'] = float_round(moves_in_res.get(product_id, 0.0), precision_rounding=rounding)
                res[product_id]['outgoing_qty'] = float_round(moves_out_res.get(product_id, 0.0), precision_rounding=rounding)
                res[product_id]['virtual_available'] = float_round(
                    qty_available + res[product_id]['incoming_qty'] - res[product_id]['outgoing_qty'],
                    precision_rounding=rounding)


            
            
            return res

    def get_lines(self,data):

      vals = []
      product_list = []
      domain_1 = [('state','=','done')]
      if data['start_date'] :
        domain_1.append(('date_expected','>=',data['start_date']))
      if data['end_date'] :

        domain_1.append(('date_expected','<=',data['end_date']))

      if data['warehouse_id'] :
        #domain_1.append(('warehouse_id','=',data['warehouse_id'].id))
        domain_1.append(('picking_id.branch_id','=',data['warehouse_id'].branch_id.id))

      #domain_1.append(('product_id','in',product_list))

      move_line_rec = self.env['stock.move'].search(domain_1)

      

      

      for pro in move_line_rec :
        if pro.product_id.id not in product_list :
          
          product_list.append(pro.product_id.id)



      domain_2 = [('state','=','done')]
      if data['start_date'] :
        domain_2.append(('inventory_id.date','>=',data['start_date']))
      if data['end_date'] :

        domain_2.append(('inventory_id.date','<=',data['end_date']))

      if data['warehouse_id'] :
        domain_2.append(('inventory_id.branch_id','=',data['warehouse_id'].branch_id.id))

      

      new_move_line_rec = self.env['stock.move'].search(domain_2)


      for pro_id in new_move_line_rec :

        if pro_id.product_id.id not in product_list :
          product_list.append(pro_id.product_id.id)



      domain_p = [('order_id.state','in',['done','paid'])]
      if data['start_date'] :
        domain_p.append(('order_id.date_order','>=',data['start_date']))
      if data['end_date'] :

        domain_p.append(('order_id.date_order','<=',data['end_date']))

      if data['warehouse_id'] :
        
        domain_p.append(('order_id.branch_id','=',data['warehouse_id'].branch_id.id))



      
      pos_line_rec = self.env['pos.order.line'].search(domain_p)

      for p in pos_line_rec :
        if p.product_id.id not in product_list :
          product_list.append(p.product_id.id)



      domain_m = [('state','=','done')]
      
      if data['warehouse_id'] :
        domain_m.append(('branch_id','=',data['warehouse_id'].branch_id.id))

      manufacturing_orders_res = self.env['mrp.production'].search(domain_m)

      for res in manufacturing_orders_res :
        manu_products = []
        for product in res.finished_move_line_ids :
          manu_products.append(product.product_id.id)

        for pick in res.picking_ids:
          if pick.state == 'done' and pick.date_done.date() >= data['start_date'] and pick.date_done.date() <= data['end_date']:

            for line in pick.move_ids_without_package :
              if line.product_id.id in manu_products :
                if line.product_id.id not in product_list :
                  product_list.append(line.product_id.id)





      for pro_id in product_list :
        pro_obj = self.env['product.product'].browse(pro_id)
        name = pro_obj.name
        uom = pro_obj.uom_id.name
        #print ("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",type(data['start_date']),'llllllllllllllllllllllllll',self.env.context)
        #pro_obj._context = dict(self.env.context, to_date=data['start_date'])
        opening = self._compute_quantities_product_quant_dic(False,data['start_date'],pro_obj,data)
        #print ("qty=ooooooooooooo======================================",opening[pro_obj.id]['qty_available'],'name=========================',pro_obj.name)
        opening_qty = opening[pro_obj.id]['qty_available']

        if opening_qty < 0:
          opening_qty =0


        
        #bal = pro_obj._compute_quantities_dict(pro_obj._context.get('lot_id'), pro_obj._context.get('owner_id'), pro_obj._context.get('package_id'), data['end_date'])
        bal = self._compute_quantities_product_quant_dic(False,data['end_date'],pro_obj,data)
        #print ("qty===bbbbbbbbbbbbbbbbbbbb====================================",opening[pro_obj.id]['qty_available'])
        
        bal_qty = bal[pro_obj.id]['qty_available']

        if bal_qty < 0 :
          bal_qty = 0

        move_line_opening = self.env['stock.move'].search([
                                                            ('state','=','done'),
                                                            ('product_id','=',pro_id),
                                                            ('warehouse_id','=',data['warehouse_id'].id)

                                                            ])
        
        incoming = 0
        outgoing = 0
        for line in move_line_opening :
          date_1 = line.date_expected.date()
          
          if date_1 == data['start_date'] :
            if line.picking_id.picking_type_id.code == 'outgoing':
              outgoing = outgoing + line.product_uom_qty

            if line.picking_id.picking_type_id.code == 'incoming':
              incoming = incoming + line.product_uom_qty









        move_line = self.env['stock.move'].search([
                                                  ('state','=','done'),
                                                  ('date_expected','>=',data['start_date']),
                                                  ('date_expected','<=',data['end_date']),
                                                   
                                                   ('product_id','=',pro_id),
                                                   ('picking_id.branch_id','=',data['warehouse_id'].branch_id.id)

                                                    ])

        inventory_adj_line = self.env['stock.inventory.line'].search([
                                                  ('inventory_id.date','>=',data['start_date']),
                                                  ('inventory_id.date','<=',data['end_date']),
                                                  ('inventory_id.branch_id','=',data['warehouse_id'].branch_id.id),
                                                  ('product_id','=',pro_id),
                                                  ('inventory_id.state','=','done')
          ])
        
        adjestment= 0
        product_list = []
        for line in inventory_adj_line :
          warehouse = self.env['stock.warehouse'].search([('branch_id','=',line.inventory_id.branch_id.id)])
          if warehouse.id == data['warehouse_id'].id :
            
            product_list.append(line.id)

          

        
        max_id = 0
        for i in product_list :
          if i > max_id :
            max_id = i

        if max_id > 0 :
          
          adjestment = self.env['stock.inventory.line'].browse(max_id).product_qty

        
        
        
        

        recived_qty = 0
        sale_qty = 0
        for line in move_line :
          if line.picking_id.picking_type_id.code == 'outgoing':
            sale_qty = sale_qty + line.product_uom_qty

          if line.picking_id.picking_type_id.code == 'incoming':
            recived_qty = recived_qty + line.product_uom_qty


          if line.picking_id.picking_type_id.code == 'internal':
            if line.location_id.usage == 'inventory'  and line.location_dest_id.usage == 'internal':
              recived_qty = recived_qty + line.product_uom_qty
          
          if line.location_id.usage == 'inventory'  :
            
            recived_qty = recived_qty + line.product_uom_qty


        
        # new_move_lines = self.env['stock.move'].search([
                                                  
        #                                           ('inventory_id.date','>=',data['start_date']),
        #                                           ('inventory_id.date','<=',data['end_date']),
        #                                           ('inventory_id.branch_id','=',data['warehouse_id'].branch_id.id),
        #                                           ('product_id','=',pro_id),
        #                                           ('inventory_id.state','=','done')
        #   ])
        
        
        # for line in new_move_lines :
          
        #   if line.location_id.usage == 'inventory'  and line.location_dest_id.usage == 'internal':
           
        #     recived_qty = recived_qty + line.product_uom_qty

       

        domain_man = [('state','=','done')]
      
        if data['warehouse_id'] :
          domain_man.append(('branch_id','=',data['warehouse_id'].branch_id.id))

        manufacturing_orders_res = self.env['mrp.production'].search(domain_man)

        for res in manufacturing_orders_res :
          

          for pick in res.picking_ids:
            if pick.state == 'done' and pick.date_done.date() >= data['start_date'] and pick.date_done.date() <= data['end_date']:

              for line in pick.move_ids_without_package :
                if line.product_id.id == pro_id :
                  recived_qty = recived_qty + line.product_uom_qty





        vals.append({'pro_name':name,
                    'description' : name,
                    'opening' : opening_qty,
                    'received' : recived_qty,
                    'sale_qty' : sale_qty,
                    'adjestment': adjestment,
                    'balance' : bal_qty,
                    'id' : pro_id,
                    'uom' : uom,

                    })


      product_res = self.env['product.product'].search([('qty_available', '!=', 0),
                                                                ('type', '=', 'product'),

                                                                ])
        
      for pro in product_res :
        if pro.id not in product_list :
          if pro.create_date.date() <= data['start_date'] :

              opening = self._compute_quantities_product_quant_dic(False,data['start_date'],pro,data)
        
              opening_qty_n = opening[pro.id]['qty_available']


              bal = self._compute_quantities_product_quant_dic(False,data['end_date'],pro,data)
        
        
              bal_qty = bal[pro.id]['qty_available']

              vals.append({'pro_name':pro.name,
                    'description' : name,
                    'opening' : opening_qty_n,
                    'received' : 0,
                    'sale_qty' : 0,
                    'adjestment': 0,
                    'balance' : bal_qty,
                    'id' : pro.id,
                    'uom' : pro.uom_id.name,

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
        title = "Inventory Movement"

        worksheet.write(1, 1,'Start Date:')
        worksheet.write(1, 2,str(self.start_date.strftime("%d-%m-%Y")))
        worksheet.write(1, 7,'End Date:')
        worksheet.write(1, 8,str(self.end_date.strftime("%d-%m-%Y")))
        

        worksheet.write(0, 1,self.warehouse_id.name)


        worksheet.write_merge(2, 2, 1, 8, title, style=style_title)
        
        worksheet.write(3, 1, 'Product', style_title)
        worksheet.write(3, 2, 'Description', style_title)
        worksheet.write(3, 3, 'UOM', style_title)
        worksheet.write(3, 4, 'Opening Balance Qty', style_title)
        worksheet.write(3, 5, 'Received Qty', style_title)
        worksheet.write(3, 6, 'Sales Qty', style_title)
        worksheet.write(3, 7, 'Adjesment Qty', style_title)
        worksheet.write(3, 8, 'Balance', style_title)
        
        data  = { 'start_date': self.start_date, 'end_date': self.end_date,
                'warehouse_id':self.warehouse_id
                }
        lines = self.get_lines(data)
        row = 4
        clos = 0
        total_opn = 0
        total_rcv = 0
        total_sl = 0
        total_adj = 0
        total_bal = 0
        for line in lines :
            worksheet.write(row, 1,line['pro_name'])
            worksheet.write(row, 2,line['description'])
            worksheet.write(row, 3,line['uom'])
            worksheet.write(row, 4,line['opening'])
            worksheet.write(row, 5,line['received'])
            worksheet.write(row, 6,line['sale_qty'])
            worksheet.write(row, 7,line['adjestment'])
            worksheet.write(row, 8,line['balance'])
            
            total_opn = total_opn + line['opening']
            total_rcv = total_rcv + line['received']
            total_sl = total_sl + line['sale_qty']
            total_adj = total_adj + line['adjestment']
            total_bal = total_bal + line['balance']
            
            row = row+1

        worksheet.write(row + 1, 3,"Total = ")
        worksheet.write(row + 1, 4,total_opn)
        worksheet.write(row + 1, 5,total_rcv)
        worksheet.write(row + 1, 6,total_sl)
        worksheet.write(row + 1, 7,total_adj)
        worksheet.write(row + 1, 8,total_bal)
    
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
    _description "Inventory Movemove Excel"
    
    excel_file = fields.Binary('Excel Report Inventory')
    file_name = fields.Char('Excel File', size=64)

