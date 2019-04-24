# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sale Purchase Invoice Discount in Odoo',
    'version': '12.0.0.9',
    'category': 'Sales',
    'sequence': 14,
    'price': '25',
    'currency': "EUR",
    'summary': 'Sales and Purchase Invoice Discount',
    'description': """
Manage sales and purchase orders and Invoice Discount Manages the Discount in Sale order , Purchase Order and in whole Sale order/Purchase order basis on Fix
and Percentage wise as well as calculate tax before discount and after
discount and same for the Invoice.
This module also have following separated features.
    -Global Discount on Invoice, Discount on purchase order, Global Discount on Sales order
    -Discount on sale order line, Discount on purchase order line, Discount on Invoice line
    -Discount purchase, Discount sale,Discount Invoice, Discount POS, Disount Order,Order Discount, Point of Sale Discount,Discont on pricelist, Fixed Discount, Percentage Discount, Commission, Discount Tax.
    -All in One Discount, All discount, Sales Discount, Purchase Discount,Sales Invoice Discount, Purchase Invoice Discount,Odoo Discount, OpenERP Discount, Sale Order Discount, Purchase order discount, Invoice line Discount,Discount with Taxes, Order line Discount, sale line discount, purchase line discount,Discount on line.Discount Feature, Discount for all

=========================================
Manages the Discount in Sale order and Purchase order line basis on Fix
and Percentage wise as well as for the Invoice.
""",

    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'images': [],
    'depends': ['base','sale','sale_management','product','stock','account','purchase'],
    'data': [
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'report/inherit_sale_report.xml',
        'report/inherit_account_report.xml',
        'report/inherit_purchase_report.xml',
        
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'images':['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
