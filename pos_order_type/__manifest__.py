# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'POS Order Type',
    'version': '1.0',
    'summary': "Manage POS order type",
    'category': 'Point Of Sale',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'www.synconics.com',
    'description': """
        Use for decide pricing as per order type(For Customer, Manager or Staff).
    """,
    'depends': ['point_of_sale'],
    'data': [
        'data/pricelist_data.xml',
        'views/point_of_sale.xml',
        'views/product_pricelist_view.xml',
        'views/res_users_view.xml',
        'views/pos_config_view.xml',
        'views/pos_order_view.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1',
}
