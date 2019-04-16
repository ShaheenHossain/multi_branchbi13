# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Multiple Branch(Unit) Operations for Manufacturing',
    'version': '12.0.0.2',
    'category': 'Manufacturing',
    'summary': 'Multiple Branches/Unit Operation on Manufacturing for single company',
    "description": """
       Multiple Unit operation management for single company, Mutiple Branch management for single company, multiple operation for single company.
    Branch for POS, Branch for Sales, Branch for Purchase, Branch for all, Branch for Accounting, Branch for invoicing, Branch for Payment order, Branch for point of sales, Branch for voucher, Branch for All Accounting reports, Branch Accounting filter.Branch for warehouse, branch for sale stock, branch for location
  Unit for POS, Unit for Sales, Unit for Purchase, Unit for all, Unit for Accounting, Unit for invoicing, Unit for Payment order, Unit for point of sales, Unit for voucher, Unit for All Accounting reports, Unit Accounting filter.branch unit for warehouse, branch unit for sale stock, branch unit for location
  Unit Operation for POS, Unit Operation for Sales, Unit operation for Purchase, Unit operation for all, Unit operation for Accounting, Unit Operation for invoicing, Unit operation for Payment order, Unit operation for point of sales, Unit operation for voucher, Unit operation for All Accounting reports, Unit operation Accounting filter.
  Branch Operation for POS, Branch Operation for Sales, Branch operation for Purchase, Branch operation for all, Branch operation for Accounting, Branch Operation for invoicing, Branch operation for Payment order, Branch operation for point of sales, Branch operation for voucher, Branch operation for All Accounting reports, Branch operation Accounting filter.


       operating unit for company.
       Multiple Branch Operation Setup for Human Resource
       Unit Operation Setup for Human Resource

       Multiple Branch Operation Setup for MRP
       Unit Operation Setup for MRP
       multiple branch for Manufacturing Order
       multiple branch for MRP BOM
       multiple branch for Production order
       multiple branch for Manufacturing Application
       multiple branch for MRP Application
       multiple branch for BOM
       multiple branch for Workorders
       multiple branch for manufacturing workorders
       multiple branch for MRP and production
       multiple branch for MRP production
       multiple branch for Manufacturing process
       multiple branch for All Manufacturing
       multiple branch for bill of material

       Unit Operation for Manufacturing Order
       Unit Operation for MRP BOM
       Unit Operation for Production order
       Unit Operation for Manufacturing Application
       Unit Operation for MRP Application
       Unit Operation for BOM
       Unit Operation for Workorders
       multiple Unit Operation for manufacturing workorders
       multiple Unit Operation for MRP and production
       multiple Unit Operation for MRP production
       multiple Unit Operation for Manufacturing process
       multiple Unit Operation for All Manufacturing
       multiple Unit Operation for bill of material
       branch mrp
       mrp branch
       mrp operating unit
       mrp unit operation management
      mrp multiple unit
       operating unit mrp
       branch manufacturing order
       manufacturing branch
       manufacturing operating unit
       manufacturing unit operation management
      manufacturing multiple unit
       operating unit manufacturing



operating Unit for POS,operating Unit for Sales,operating Unit for Purchase,operating Unit for all,operating Unit for Accounting,operating Unit for invoicing,operating Unit for Payment order,operating Unit for point of sales,operating Unit for voucher,operating Unit for All Accounting reports,operating Unit Accounting filter. Operating unit for picking, operating unit for warehouse, operaing unit for sale stock, operating unit for location
operating-Unit Operation for POS,operating-Unit Operation for Sales,operating-Unit operation for Purchase,operating-Unit operation for all, operating-Unit operation for Accounting,operating-Unit Operation for invoicing,operating-Unit operation for Payment order,operating-Unit operation for point of sales,operating-Unit operation for voucher,operating-Unit operation for All Accounting reports,operating-Unit operation Accounting filter.
    """,
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    "price": 40,
    "currency": 'EUR',
    'depends': ['base','branch','mrp'],
    'data': [
                'security/ir.model.access.csv',
                'security/mrp_branch_security.xml',
                'views/mrp_branch_view.xml',
                'report/manufacturing_report_view.xml',
             ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/zXhUMtmgxvI',
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
