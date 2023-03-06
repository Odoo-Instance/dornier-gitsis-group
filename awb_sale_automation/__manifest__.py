# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'AWB Sales Automation',
    'version' : '15.0.1',
    'summary': 'AWB Sales Automation',
    'sequence': 10,
    'description': 
            """
                Sales
                ====================
                AWB Sales Automation 
            """,
    'category': 'Sales',
    'depends' : ['sale', 'sale_management'],
    'data': [
        "views/res_config_settings_views.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
