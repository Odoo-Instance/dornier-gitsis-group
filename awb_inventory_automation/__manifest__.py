# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'AWB Inventory Automation',
    'version' : '15.0.1',
    'summary': 'AWB Inventory Automation',
    'sequence': 10,
    'description': 
            """
                Inventory
                ====================
                AWB Inventory Automation 
            """,
    'category': 'Inventory',
    'depends' : ['stock'],
    'data': [
        "views/res_config_settings_views.xml",
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
