# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'author':  'Dennis Boy Silva - (Agilis Enterprise Solutions Inc.)',
    'website': 'agilis-solutions.com',
    'license': 'AGPL-3',
    'category': 'Tool',
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase.xml',
        'views/invoice.xml',
        ],
    'depends': [
            'base',
            'account',
            'purchase',
            'hr_company_profile',
            'sale_tax_ph_standard',
        ],
    'description': '''
Added the following fields on Purchase Order Lines
    * Purchase Category
Added the following fields on Purchase Invoice Lines
    * Purchase Category''',
    'installable': True,
    'auto_install': False,
    'name': "Purchase Tax Philippines Standard",
    'summary': 'localizing (PH) the Purchase transaction',
    'test': [],
    'version': '8.0.0'
}
