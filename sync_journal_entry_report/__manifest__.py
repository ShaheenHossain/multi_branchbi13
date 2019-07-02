# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details

{
    'name': 'Journal Entry Report',
    'summary': """Generate Journal Report """,
    'version': '1.0',
    'description': """Generate Journal Report""",
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'http://www.synconics.com',
    'category': 'Accounting',
    'depends': ['account'],
    'license': 'OPL-1',
    'data': [
        'views/journal_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}