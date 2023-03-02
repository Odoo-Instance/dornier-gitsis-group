# -*- coding: utf-8 -*-

{
    'name': 'Facebook Product Cataclog ',
    'summary': '''Create a product feed url for facebook''',
    'version': '15.0.1.0.1',
    'author': "Achieve Without Borders, Inc",
    'website': '"http://www.achievewithoutborders.com"',
    'license': "OPL-1",
    'website': 'http://www.srikeshinfotech.com',
    'description': """
        Facebook product catalog 
    """,
    'images': [],
    
    'depends': ['base','website','stock','product','website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/google_category.xml',
        'views/fb_fields.xml',
        'views/field_mapping.xml',
        'views/fb_catalog_shop.xml',
        'views/product_template.xml',
        'views/template.xml',
        'data/product_data_update.xml',
       ],
    'qweb': [],
    'demo': [],
    'assets': {
            'web.assets_qweb': [
                    'facebook_product_catelog/static/src/xml/**/*',            
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': True,
}
