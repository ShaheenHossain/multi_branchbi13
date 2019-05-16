# -*- coding: utf-8 -*-
# Part of Synconics. See LICENSE file for full copyright and licensing details.

{
    'name': "Stock Inventory Report",
    'version': '1.0',
    'category': 'Warehouse',
    'summary': 'Stock Movement Report In Excel',
    'description': """
    Stock Movement Report In Excel
    """,
    'author': 'Synconics Technologies Pvt. Ltd',
    'website': 'http://www.synconics.com',
    'depends': ['stock', 'sale_management', 'purchase', 'bi_odoo_mrp_multi_branch'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/stock_inventory_view.xml',
        'report/report_stock_inventory_template.xml',
        'report/stock_inventory_report.xml',
        'views/inventory_movement_pivot_report.xml'
    ],
    'images': [
        'static/description/main_screen.jpg',
    ],
    'price': 0.0,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}