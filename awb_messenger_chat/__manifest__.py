# -*- coding: utf-8 -*-

{
    'name': """Facebook Messenger Chat  Odoo Integration""",
    'summary': '''Chat with us through messenger''',
    'version': '15.0.1.0.1',
    'category': 'Website',
    'website': "http://www.achievewithoutborders.com",
    'author': 'Achieve Without Borders, Inc',
    'license': 'LGPL-3',

    'depends': ['base', 'website','crm_iap_mine'],

    'data': [
            'views/website.xml',
            'views/res_config_settings.xml',
            'views/templates.xml',
            
    ],
    'assets':{
            'web.assets_backend': [
                'awb_messenger_chat/static/src/components/fb_chat.js',
                ],
            'web.assets_qweb': [
            
            'awb_messenger_chat/static/src/components/fb_chat.xml',
            
        ],
    },
    

    
    
    'currency': 'EUR',

    'application': True,
    'auto_install': False,
    'installable': True,
}
