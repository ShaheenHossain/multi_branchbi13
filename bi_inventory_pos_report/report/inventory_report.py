# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import models, api






class inventory_pdf_report(models.AbstractModel):
    _name = 'report.bi_inventory_pos_report.inventory_pdf_template'
    
    @api.multi
    def _get_report_values(self, docids, data=None):
        data = data if data is not None else {}
        docs = self.env['inventory.report.wizard'].browse(docids)
        data  = { 'start_date': docs.start_date, 'end_date': docs.end_date,
                'warehouse_id':docs.warehouse_id,'transfer_in_out':docs.transfer_in_out
                }
        
        return {
                   'doc_model': 'inventory.report.wizard',
                   'data' : data,

                   
                   'get_lines':self._get_lines(data),
                   
                   }


    def _get_lines(self,data):

      vals = []
      domain = [('state','=','done')]
      if data['start_date'] :
        domain.append(('scheduled_date','>=',data['start_date']))
      if data['end_date'] :

        domain.append(('scheduled_date','<=',data['end_date']))

      if data['warehouse_id'] :
        domain.append(('picking_type_id.warehouse_id','=',data['warehouse_id'].id))

      if data['transfer_in_out'] :
        domain.append(('picking_type_id.code','=',data['transfer_in_out']))
      stock_picking_rec = self.env['stock.picking'].search(domain)

      

      for res in stock_picking_rec :
        product_list = []
        for line in res.move_ids_without_package :

          vals.append({'warehouse_name' : data['warehouse_id'].name,
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


