# -*- coding: utf-8 -*-
"""imports from odoo"""
from odoo import fields, models


class FieldMapping(models.Model):
    """variable declaration"""
    _name = 'awb.field.mapping'
    _description = "Field Mapping"
 
    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(string="Active",default=True )
    mapping_line_ids = fields.One2many('awb.field.mapping.line','mapping_id', string="mapping_line")
    
class FieldMappingLine(models.Model):
    """variable declaration"""
    _name = 'awb.field.mapping.line'
    _description = "Field Mapping line"
    
    fb_field_id = fields.Many2one('awb.fb.fields', string= "Facebook Fields", required=True)
    product_model_id = fields.Many2one('ir.model.fields', string="Model Field", domain = [('model', '=', 'product.template')])
    default_f = fields.Char(string="Default")
    fixed_f = fields.Boolean(string="Fixed")
    fixed_field_text = fields.Char(String="Fixed Text")
    name = fields.Char(string="Name")
    mapping_id = fields.Many2one('awb.field.mapping', string="Mapping")
    
    