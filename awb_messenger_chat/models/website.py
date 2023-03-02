# -*- coding: utf-8 -*-
"""imports from odoo lib"""
from odoo import fields, models

class Website(models.Model):  # @UndefinedVariable
    """Variable declaration"""
    _inherit = 'website'

    facebook_page_id = fields.Char('Facebook Page ID',copy=False,tracking=False,index=False,required=False,translate=True)  # @UndefinedVariable
    
