# -*- coding: utf-8 -*-
"""imports from odoo lib"""
from odoo import fields, models

class Website(models.Model):  # @UndefinedVariable
    """Variable declaration"""
    _inherit = 'website'

    facebook_pixel_key = fields.Char('Facebook Pixel ID')  # @UndefinedVariable
    facebook_domain_verification_code = fields.Char(string='Verification Code', help='Facebook Domain Verification Code',)  # @UndefinedVariable
