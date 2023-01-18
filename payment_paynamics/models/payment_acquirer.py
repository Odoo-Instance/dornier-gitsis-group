# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

import requests
from werkzeug import urls

from odoo import _, api, fields, models, service
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('paynamics', 'Paynamics')], ondelete={'paynamics': 'set default'})
    paynamics_seller_account = fields.Char(
        'Merchant ID', groups='base.group_user',
        help='The Merchant ID is used to ensure communications coming from \
            Paynamics are valid and secured.')
    paynamics_pdt_token = fields.Char(string='Merchant Key', help='Payment Data \
        Transfer allows you to receive notification of successful payments as \
        they are made.', groups='base.group_user')
    
    paynamics_user = fields.Char(string='Merchant User', help='Payment Data \
        Transfer allows you to receive notification of successful payments as \
        they are made.', groups='base.group_user')
    
    paynamics_password = fields.Char(string='Merchant Password', help='Payment Data \
        Transfer allows you to receive notification of successful payments as \
        they are made.', groups='base.group_user')
    
    paynamics_checkout_url = fields.Char(string='Checkout URL', help='Payment Data \
        Transfer allows you to receive notification of successful payments as \
        they are made.', groups='base.group_user')
    
    paynamics_cash = fields.Boolean(string="Cash", default=True)
    paynamics_creditcard = fields.Boolean(string="Credit Card", default=True)
    paynamics_allchannel = fields.Boolean(string="All Payment Channel", default=False)
    paynamics_online = fields.Boolean(string="Online Payment", default=False)

    #=== BUSINESS METHODS ===#

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider != 'paynamics':
            return super()._get_default_payment_method_id()
        return self.env.ref('payment_paynamics.payment_method_paynamics').id

