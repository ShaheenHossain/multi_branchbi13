# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Inventory POS Report",
    "version" : "12.0.0.1",
    "category" : "",
    'summary': 'Inventory POS Report',
    "description": """
    """,
    "author": "BrowseInfo",
    "website" : "www.browseinfo.in",
    "price": 000,
    "currency": 'EUR',
    "depends" : ['base','branch','stock'],
    "data": ["security/ir.model.access.csv",
            "wizard/inventory_wizard_views.xml",
            "wizard/inventory_movement_wizard_view.xml",
            "wizard/pos_wizard_view.xml",
            'wizard/pos_fast_moving_wizard.xml',
            'report/inventory_report_trmplate.xml',
            'report/inventory_movement_template.xml',
            'report/pos_fast_moving_template.xml',
            'report/pos_template.xml',
            'report/report_views.xml',
            'views/inventory_pivot_view.xml',
        
    ],
    'qweb': [
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url":'youtube link',
    "images":["static/description/Banner.png"],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
