# -*- coding: utf-8 -*-
{
    'name': "Signature Creator",
    'version': '11.0.0.1',
    'summary': 'Signature Creator',
    'sequence': 2,
    'description': """
Odoo Module
===========
Specifically Designed for Etisalat-TBPC

Signatory Creator
---------------------
Automatically create signature for individual people, and able to create a signature form with size 
2 by x where x is any number of rows.
    """,
    'author': "Marc Philippe de Villeres",
    'website': "https://github.com/mpdevilleres",
    'category': 'TBPC Budget',
    'depends': [
        'base'
    ],
    'data': [
        'security/budget_signature.xml',
        'security/ir.model.access.csv',

        'views/signatory.xml',
        'views/menu.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
