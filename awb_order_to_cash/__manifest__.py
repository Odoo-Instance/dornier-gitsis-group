# -*- coding: utf-8 -*-

{
    'name': """Order to Cash Automation""",
    'summary': '''Automation for order to cash.''',
    'version': '15.0.1.0.3',
    'category': 'sales',
    'website': "http://www.achievewithoutborders.com",
    'author': 'Achieve Without Borders, Inc',
    'license': 'LGPL-3',

    'depends': ['base','sale','purchase', 'website','stock','product','website_sale'],

    'data': [
           'views/pay_sale_order.xml',
           'views/res_partner.xml',
           'views/res_config.xml',
           'views/sale_order_new.xml',
           'views/account_move.xml',
           'data/template.xml',
           'data/cron.xml',
    ],
    'assets':{
            'web.assets_backend': [
                
                ],
            'web.assets_qweb': [
                    
        ],
    },
    

    
    
    'currency': 'EUR',

    'application': True,
    'auto_install': False,
    'installable': True,
}
