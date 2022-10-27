# -*- coding: utf-8 -*-

{
    'name': 'Paynamics Payment Acquirer',
    'category': 'Accounting/Payment',
    'summary': 'Payment Acquirer: Paynamics Implementation',
    'author': 'Srikesh Infotech',
    'license': "OPL-1",
    'website': 'http://www.srikeshinfotech.com',
    'version': '1.0',
    'description': """Paynamics Payment Acquirer""",
    'depends': ['payment'],
    'images': ['images/main_screenshot.png'],
    'price': 200,
    'currency': 'USD',
    'data': [
        'views/payment_views.xml',
        'views/payment_paynamics_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'installable': True,
    'post_init_hook': 'create_missing_journal_for_acquirers',
}
