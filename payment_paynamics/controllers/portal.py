# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment import utils as payment_utils
from odoo.addons.portal.controllers import portal


class CustomerPortal(portal.CustomerPortal):

    def _create_transaction(self, *args, custom_create_values=None, paynamics_method=None, **kwargs):
        if paynamics_method:
            if custom_create_values is None:
                custom_create_values = {}
            custom_create_values['paynamics_method'] = paynamics_method
        return super()._create_transaction(
            *args, custom_create_values=custom_create_values, **kwargs
        )
