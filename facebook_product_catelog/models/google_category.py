# -*- coding: utf-8 -*-
"""imports from odoo"""
from odoo import fields, models


class GoogleCategory(models.Model):
    """variable declaration"""
    _name = 'awb.google.category'
    _description = "Google Category"
    _rec_name = 'google_category_name'
    
    google_category_name = fields.Char(String="Google Category Name")
    g_cate_id = fields.Integer(String="Category Id")
    