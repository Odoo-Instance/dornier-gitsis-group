# -*- coding: utf-8 -*-

{
    'name': """Facebook Pixel Odoo Integration""",
    'summary': '''Track and Check Analytics in Facebook Analytics Using Facebook Pixel''',
    'version': '15.0.1.0.1',
    'category': 'Website',
    'website': "http://www.achievewithoutborders.com",
    'author': 'Achieve Without Borders, Inc',
    'license': 'LGPL-3',

    'depends': ['base', 'website',],

    'data': [
        'views/templates.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets':{
            'web.assets_frontend': [
                'awb_facebook_pixel/static/src/js/fb_events.js',
                
                ],
    },
    

    
    
    'currency': 'EUR',

    'application': True,
    'auto_install': False,
    'installable': True,
}
