# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"
    
    import_id = fields.Char(string="Import ID")
    
class ProductCategory(models.Model):
    _inherit = "product.category"
    
    import_id = fields.Char(string="Import ID")
    
class ProductUOM(models.Model):
    _inherit = "uom.uom"
    
    import_id = fields.Char(string="Import ID")
    
    
class ProductAttribute(models.Model):
    _inherit = "product.attribute"
    
    import_id = fields.Char(string="Import ID")
    
class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    import_id = fields.Char(string="Import ID")
    
class ResPartner(models.Model):
    _inherit = "res.partner"
    
    import_id = fields.Char(string="Import ID")
    
    