# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Financial Reports For Branch -Enterprise Edition Odoo",
    "version" : "12.0.0.3",
    "category" : "Accounting",
    'summary': 'This app helps to provide branch wise filter on all Financial statement for Enterprise edition',
    "description": """
      multiple branch accounting reports
      multiple branch accounting enterprise reports
      multiple branch enterprise accounting reports
      multiple branch with accounting reports
      multiple branch enterprise accounting reports

      multiple unit accounting reports
      multiple unit accounting enterprise reports
      multiple unit enterprise accounting reports
      multiple unit with accounting reports
      multiple unit enterprise accounting reports

      multiple unit operation accounting reports
      multiple unit operation enterprise reports
      multiple unit operation enterprise accounting reports
      multiple unit operation with accounting reports
      multiple unit operation enterprise accounting reports

       Multiple Unit operation management for single company, Mutiple Branch management for single company, multiple operation for single company. Financial Reports , Financial filter Reports, accounting Financial Reports, accounting filter report
	   branch Financial Reports , branch Financial Reports , multiple company accounting report , finacial report filter report
    Branch for POS, Branch for Sales, Branch for Purchase, Branch for all, Branch for Accounting, Branch for invoicing, Branch for Payment order, Branch for point of sales, Branch for voucher, Branch for All Accounting reports, Branch Accounting filter.
  Unit for POS, Unit for Sales, Unit for Purchase, Unit for all, Unit for Accounting, Unit for invoicing, Unit for Payment order, Unit for point of sales, Unit for voucher, Unit for All Accounting reports, Unit Accounting filter.
  Unit Operation for POS, Unit Operation for Sales, Unit operation for Purchase, Unit operation for all, Unit operation for Accounting, Unit Operation for invoicing, Unit operation for Payment order, Unit operation for point of sales, Unit operation for voucher, Unit operation for All Accounting reports, Unit operation Accounting filter.
  Branch Operation for POS, Branch Operation for Sales, Branch operation for Purchase, Branch operation for all, Branch operation for Accounting, Branch Operation for invoicing, Branch operation for Payment order, Branch operation for point of sales, Branch operation for voucher, Branch operation for All Accounting reports, Branch operation Accounting filter. Branch Fiancial Statement for Enterprise reports.

       Multiple Unit operation management for single company, Mutiple Branch management for single company, multiple operation for single company.
    Branch for POS, Branch for Sales, Branch for Purchase, Branch for all, Branch for Accounting, Branch for invoicing, Branch for Payment order, Branch for point of sales, Branch for voucher, Branch for All Accounting reports, Branch Accounting filter.Branch for warehouse, branch for sale stock, branch for location
  Unit for POS, Unit for Sales, Unit for Purchase, Unit for all, Unit for Accounting, Unit for invoicing, Unit for Payment order, Unit for point of sales, Unit for voucher, Unit for All Accounting reports, Unit Accounting filter.branch unit for warehouse, branch unit for sale stock, branch unit for location
  Unit Operation for POS, Unit Operation for Sales, Unit operation for Purchase, Unit operation for all, Unit operation for Accounting, Unit Operation for invoicing, Unit operation for Payment order, Unit operation for point of sales, Unit operation for voucher, Unit operation for All Accounting reports, Unit operation Accounting filter.
  Branch Operation for POS, Branch Operation for Sales, Branch operation for Purchase, Branch operation for all, Branch operation for Accounting, Branch Operation for invoicing, Branch operation for Payment order, Branch operation for point of sales, Branch operation for voucher, Branch operation for All Accounting reports, Branch operation Accounting filter.

       operating unit for company.
       Multiple Branch Operation Setup for Project Management
       Unit Operation Setup for Project Management

       Multiple Branch Operation Setup for Project Task management
       Unit Operation Setup for Task management
       multiple branch for Project Costing
       multiple branch for Project Task
       multiple branch for Task management
       multiple branch for Issue
       multiple branch for Project Application
       multiple branch for Project issue
       multiple branch for PMS

       Unit Operation for Project management
       Unit Operation for Project Costing
       Unit Operation for Task management
       Unit Operation for Project Issue
       Unit Operation for Project task
       Unit Operation for Issue
       Unit Operation for Project Application
       multiple Unit Operation for Project management
       multiple Unit Operation for Project Costing
       multiple Unit Operation for Task management
       multiple Unit Operation for Project Issue
       multiple Unit Operation for Project Task
       multiple Unit Operation for Project Application


operating Unit for POS,operating Unit for Sales,operating Unit for Purchase,operating Unit for all,operating Unit for Accounting,operating Unit for invoicing,operating Unit for Payment order,operating Unit for point of sales,operating Unit for voucher,operating Unit for All Accounting reports,operating Unit Accounting filter. Operating unit for picking, operating unit for warehouse, operaing unit for sale stock, operating unit for location
operating-Unit Operation for POS,operating-Unit Operation for Sales,operating-Unit operation for Purchase,operating-Unit operation for all, operating-Unit operation for Accounting,operating-Unit Operation for invoicing,operating-Unit operation for Payment order,operating-Unit operation for point of sales,operating-Unit operation for voucher,operating-Unit operation for All Accounting reports,operating-Unit operation Accounting filter.

    """,
    "author": "BrowseInfo",
    "website" : "www.browseinfo.in",
    "price": 99,
    "currency": 'EUR',
    "depends" : ['account', 'account_accountant', 'account_reports','branch'],
    "data": [
            'data/account_financial_report_data.xml',
            'views/search_template_view.xml',
            ],
    'qweb': [],
    "auto_install": False,
    "installable": True,
    'live_test_url':'https://youtu.be/6OjItOxfGhI',
    "images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
