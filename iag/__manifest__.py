# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "IAG Customization",
    'summary': 'Barter Payment, Petty Cash and APV Report',
    'category': 'Accounting',
    'author': 'Dyan Estacio, Ralf Cabarogias',
    'sequence': 1,
    'version': '1.0',
    'depends': [
        'base','account_accountant'
        ],
    'data': [
        'report/apv.xml',
        'report/apv_customized_report.xml',
        'views/vendor_bills.xml',
        'views/delivery_slip_inherit.xml',
        'report/po.xml',
        'report/sp.xml',
        'report/check_voucher.xml',

    ],
	'installable': True,
    'application': False,

}
