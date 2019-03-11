# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "POS Logo on Session and Receipt in odoo",
    "version" : "12.0.0.2",
    "category" : "Point of Sale",
    "price": 10,
    "currency": 'EUR',
    "depends" : ['base','sale','point_of_sale'],
    "author": "BrowseInfo",
    'summary': 'Change Company Logo in Point of Sale Session and Receipt',
    "description": """
            BrowseInfo developed a new odoo/OpenERP module apps. pos logo, point of sales logo, logo  on receipt , logo change on pos
        	This Module is for Change Company Logo in Point of Sale.
            Add logo on POS, Logo Change on point of sale, Logo change on POS, Change logo on POS.
            POS Logo change, POS logo on Receipt, POS logo on Session
    """,
    "website" : "www.browseinfo.in",
    "data": [
        'views/custom_pos_view.xml',
    ],
    'qweb': ['static/src/xml/pos_logo_change.xml',],
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://youtu.be/RLEkmLUs2MY',
    "images":['static/description/Banner.png'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
