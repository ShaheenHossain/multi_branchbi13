# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "POS multi ticket and report",
    "version" : "12.0.0.3",
    "category" : "",
    'summary': 'Brief description of the module',
    "description": """
    
   Description of the module. 
    
    """,
    "author": "BrowseInfo",
    "website" : "www.browseinfo.in",
    "price": 000,
    "currency": 'EUR',
    "depends" : ['base','point_of_sale'],
    "data": [
        # 'security/sample_security.xml',
        # 'security/ir.model.access.csv',
        'report/report_view.xml',
        # 'data/data.xml',
        'wizard/pos_report_wizard_view.xml',
        'views/pos_ticket_view.xml',
        'views/assets.xml', 
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    "auto_install": False,
    "installable": True,
    # "live_test_url":'youtube link',
    # "images":["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
