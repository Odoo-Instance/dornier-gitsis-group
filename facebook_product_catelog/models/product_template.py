# -*- coding: utf-8 -*-
"""imports from odoo"""
from odoo import fields, models


class FbFields(models.Model):
    """variable declaration"""
    _inherit = 'product.template'
    _description = "Product Template"
    
    awb_google_categ_id = fields.Many2one('awb.google.category', string="Google Category")
    awb_brand = fields.Char(string="Brand")
    awb_gtin = fields.Char(string="GTIN")
    awb_mpno = fields.Char(string="Mpno")
    image_link = fields.Char(string = "Image URL")
    awb_condition = fields.Char(string = "Condition")