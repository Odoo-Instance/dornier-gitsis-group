# -*- coding: utf-8 -*-

{
    'name': 'Paynamics Payment Acquirer odoo15',
    'version': '1.0',
    'category': 'Accounting/Payment Acquirers',
    'sequence': 356,
    'summary': 'Payment Acquirer: Paynamics Implementation',
    'description': """Paynamics Payment Acquirer""",

    'author': 'AWB',
    'website': '',

    'depends': ['payment','partner_firstname'],
    'data': [
        'views/payment_paynamics_templates.xml',
        'views/payment_views.xml',
        'views/payment_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'payment_paynamics/static/src/js/payment_processing.js',
        ],
    },
    
    
    'application': True,
    'license': 'LGPL-3'
}
