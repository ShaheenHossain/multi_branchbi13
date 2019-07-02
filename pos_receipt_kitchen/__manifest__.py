# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'POS Kitchen Receipt',
    'version': '1.0',
    'summary': 'Allows to print kitchen receipt with customer receipt from pos screen',
    'category': 'Point Of Sale',
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'www.synconics.com',
    'description': """
        Allows to print kitchen receipt with customer receipt from pos screen
    """,
    'depends': ['bi_pos_multi_ticket', 'pos_logo_change'],
    'data': [],
    'qweb': ['static/src/xml/pos.xml'],
    'images': [],
    'price': 0.0,
    'currency': 'EUR',
    'auto_install': False,
    'application': True,
    'installable': True,
    'license': 'OPL-1',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
