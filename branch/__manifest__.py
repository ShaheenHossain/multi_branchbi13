# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Multiple Branch(Unit) Operation Setup for All Applications Odoo/OpenERP',
    'version': '12.0.2.1',
    'category': 'Sales',
    'author': 'BrowseInfo',
    'summary': 'Multiple Branch/Unit Operation on Sales,Purchases,Accounting/Invoicing,Voucher,Paymemt,POS, Accounting Reports for single company',
    "description": """
       Multiple Unit operation management for single company, Mutiple Branch management for single company, multiple operation for single company. branching company in odoo , mutliple store ,mutliple company in odoo , 
    Branch for POS, Branch for Sales, Branch for Purchase, Branch for all, Branch for Accounting, Branch for invoicing, Branch for Payment order, Branch for point of sales, Branch for voucher, Branch for All Accounting reports, Branch Accounting filter.Branch for warehouse, branch for sale stock, branch for location
  Unit for POS, Unit for Sales, Unit for Purchase, Unit for all, Unit for Accounting, Unit for invoicing, Unit for Payment order, Unit for point of sales, Unit for voucher, Unit for All Accounting reports, Unit Accounting filter.branch unit for warehouse, branch unit for sale stock, branch unit for location
  Unit Operation for POS, Unit Operation for Sales, Unit operation for Purchase, Unit operation for all, Unit operation for Accounting, Unit Operation for invoicing, Unit operation for Payment order, Unit operation for point of sales, Unit operation for voucher, Unit operation for All Accounting reports, Unit operation Accounting filter.
  Branch Operation for POS, Branch Operation for Sales, Branch operation for Purchase, Branch operation for all, Branch operation for Accounting, Branch Operation for invoicing, Branch operation for Payment order, Branch operation for point of sales, Branch operation for voucher, Branch operation for All Accounting reports, Branch operation Accounting filter.
       branch helpdesk and support
       branch support and helpdesk
       helpdesk branch
       helpdesk unit 
       helpdek multiple unit
       helpdesk operation unit
       branch crm
       crm branch
       crm operating unit
       crm unit operation management
       crm multiple unit
       operating unit crm
       branch Subscription
       branch contract
       Subscription branch management
       contract branch management
       operating unit Subscription
       operating unit contract
       Subscription unit management
       contract unit management
       Subscription operating unit management
       contract operating unit management

       operating unit for company.

operating Unit for POS,operating Unit for Sales,operating Unit for Purchase,operating Unit for all,operating Unit for Accounting,operating Unit for invoicing,operating Unit for Payment order,operating Unit for point of sales,operating Unit for voucher,operating Unit for All Accounting reports,operating Unit Accounting filter. Operating unit for picking, operating unit for warehouse, operaing unit for sale stock, operating unit for location
operating-Unit Operation for POS,operating-Unit Operation for Sales,operating-Unit operation for Purchase,operating-Unit operation for all, operating-Unit operation for Accounting,operating-Unit Operation for invoicing,operating-Unit operation for Payment order,operating-Unit operation for point of sales,operating-Unit operation for voucher,operating-Unit operation for All Accounting reports,operating-Unit operation Accounting filter.
    """,
    'website': 'http://www.browseinfo.in',
    'depends': ['base','sale_management','purchase','stock','account','point_of_sale','purchase_stock'],
    'data': [
                'security/branch_security.xml',
                'security/ir.model.access.csv',
                'views/res_branch_view.xml',
                'views/inherited_res_users.xml',
                'views/inherited_sale_order.xml',
                'views/inherited_stock_picking.xml',
                'views/inherited_stock_move.xml',
                'views/inherited_account_invoice.xml',
                'views/inherited_purchase_order.xml',
                'views/inherited_stock_warehouse.xml',
                'views/inherited_stock_location.xml',
                'views/inherited_account_bank_statement.xml',
                'wizard/inherited_account_payment.xml',
                'views/inherited_stock_inventory.xml',
                'views/inherited_pos_config.xml',

             ],
    'qweb': [
         'static/src/xml/pos.xml',
    ],
    'demo': [],
    "price": 239.00,
    "currency": 'EUR',
    'test': [],
    'installable': True,
    'live_test_url':'https://youtu.be/f-nqKb_jELg',
    'auto_install': False,
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
