# -*- coding: utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

{
    'name': 'Biztech Sale Coupon Customization',
    'summary': """Sale coupon Adding New Category""",
    'description': """Adding New Discount type on Discount Sale Coupan""",
    'category': 'Sales',
    'license': 'OEEL-1',
    'version': '12.0.1.0.0',
    'author': 'AppJetty',
    'website': 'https://www.appjetty.com',
    'depends': [
        'sale_coupon',
    ],
    'data': [
        'views/sale_coupon_customization.xml',
    ],
    'application': True,
    'installable': True,
}
