# -*- coding: utf-8 -*-
{
    'name': "Signature",
    'version': '0.1',
    'summary': 'Signature Creator',
    'sequence': 2,
    'description': """
Odoo Module
===========
Specifically Designed for Etisalat-TBPC

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
