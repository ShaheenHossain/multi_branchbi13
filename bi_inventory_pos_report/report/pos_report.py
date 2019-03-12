# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import models, api






class pos_pdf_report(models.AbstractModel):
    _name = 'report.bi_inventory_pos_report.pos_pdf_template'
    
    @api.multi
    def _get_report_values(self, docids, data=None):
        data = data if data is not None else {}
        docs = self.env['pos.report.wizard'].browse(docids)
        data  = { 'start_date': docs.start_date, 'end_date': docs.end_date,
                'warehouse_id':docs.warehouse_id
                }
        data1  = { 'start_date': docs.start_date.strftime("%d-%m-%Y"), 'end_date': docs.end_date.strftime("%d-%m-%Y"),
                'warehouse_id':docs.warehouse_id
                }
        return {
                   'doc_model': 'pos.report.wizard',
                   'data' : data1,

                   
                   'get_lines':self._get_lines(data),
                   'get_payments' : self._get_payments(data)
                   
                   }



    def _get_payments(self,data):
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






    def _get_lines(self,data):
      res_config= self.env['res.config.settings'].search([],order="id desc", limit=1)
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
                      'discount' : (line.qty*line.discount*line.price_unit)/100,
                      'net_sales' : line.price_subtotal,
                      'vat' : line.price_subtotal_incl - line.price_subtotal,
                      'total' : line.price_subtotal_incl
                      })


     
      return vals


