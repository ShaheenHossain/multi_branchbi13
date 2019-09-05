# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'POS Product Combo',
    'version': '1.0',
    'summary': 'Product can be sold as a Combo in POS',
    'sequence': 30,
    'description': """
Product can be sold as a Combo in POS.
    """,
    'category': 'Point Of Sale',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'www.synconics.com',
    'depends': ['pos_restaurant'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/point_of_sale.xml',
        'report/combo_invoice_report.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'currency': 'EUR',
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}
