# -*- coding: utf-8 -*-
"""imports from odoo"""
from odoo import fields, models


class FbFields(models.Model):
    """variable declaration"""
    _name = 'awb.fb.fields'
    _description = "Facebook fields"
    
    name = fields.Char(string="Fields")
    required = fields.Boolean(string="Required")
    required_g  = fields.Boolean(string="Include g")