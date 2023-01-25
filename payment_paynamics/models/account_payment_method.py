# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['paynamics'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res
    
    
class AccountPaymentIcon(models.Model):
    _inherit = 'payment.icon'

    paynamics_cash = fields.Boolean(string="Wallet")
    paynamics_creditcard = fields.Boolean(string="Credit Card")
    paynamics_allchannel = fields.Boolean(string="All Payment Channel", default=False)
    paynamics_online = fields.Boolean(string="Online Payment", default=False)
