# -*- coding: utf-8 -*-
"""imports from python lib"""
from datetime import datetime
import pandas as pd # @UnusedImport
import os  # @UnusedImport
import os.path
import shutil
import tempfile# @UnusedImport
import csv# @UnusedImport
#import PyRSS2Gen
import xml.etree.ElementTree as ET# @UnusedImport
import base64
from odoo.http import request
from lxml import etree  # @UnusedImport

"""imports from odoo"""
from odoo import fields, models, api

DATE_FORMAT = '%Y-%m-%d %H:%M'
FEED_MIMETYPE = 'application/xml; charset=utf-8'
API_SERVICE_NAME = 'sheets'
API_VERSION = 'v4'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class FbCatalog(models.Model):
    """variable declaration, created new fields"""
    _name = 'awb.fb.catalog'
    _description = "Facebook catalog"
    
    def _default_awb_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return base_url
    
    name = fields.Char(string="Name")
    awb_pricelist_id = fields.Many2one('product.pricelist', string="Pricelist")
    awb_currency_id= fields.Many2one('res.currency',string="Currency")
    website_id = fields.Many2one('website', ondelete='cascade',string="Website")
    awb_warehouse_id = fields.Many2one('stock.warehouse',string="Warehouse")
    awb_content_language_id = fields.Many2one('res.lang',string="Language")
    awb_shop_url = fields.Char(string="URL", default=_default_awb_url)
    awb_field_mapping_id = fields.Many2one('awb.field.mapping',string="Field Mapping")
    awb_feed_url = fields.Char(string="Feed URL", readonly = True)
    awb_limit = fields.Integer(string="Limit")
    awb_security = fields.Selection([('automatic', 'Automatic')], default='automatic')
    awb_product_selection_type = fields.Selection([('manual', 'Manual'),('category', 'Category')], default='category')
    awb_public_category_ids = fields.Many2many('product.public.category', string="Category")
    awb_domain = fields.Char(string="Domain")
    awb_product_rel_ids = fields.Many2many('product.template', string='Products',domain="[('sale_ok', '=', True),('website_published','=',True)]")
    awb_rel_name = fields.Char(compute='_compute_product')
    
    
    """Update new method for creating feed for facebook"""
    @api.model
    def create(self, vals):
        """create method"""
        new_vals = {}
        newResult = self.generate_feedfb(vals, new_vals)
        vals['awb_feed_url'] = newResult.get('url')
        res = super(FbCatalog, self).create(vals)
        attach = newResult.get('ir_attach')
        attach.res_id = res.id
        attach.res_model = 'awb.fb.catalog'
        return res
    
  
    def write(self, vals):
        """write method"""
        new_vals = {}
        newResult = self.generate_feedfb(new_vals,vals)
        vals['awb_feed_url'] = newResult.get('url')
        res = super(FbCatalog, self).write(vals)
        return res
    
    
    def generate_feedfb(self, vals, new_vals):
        """Used for Creating feed URL for google product. updated if condition for update product"""
        
        product_ids = []
        env = request.env
        context = request.context
        url = '/fb-shopping.xml'  # @UnusedVariable
        content = 'facebook'
        if (vals.get('awb_product_selection_type') == 'category') or (new_vals.get('awb_product_selection_type') == 'category'):
            if (vals.get('awb_public_category_ids') and (vals.get('awb_public_category_ids')[0][2] != [])) :
                product_int = vals.get('awb_public_category_ids')[0][2]
                product_template = self.env['product.template'].search([('public_categ_ids','in',product_int)])
                #product_template = self.env['product.template'].search([('categ_id','in',product_int)])
                for i in product_template: product_ids.append(i.id)
            elif (new_vals.get('awb_public_category_ids') and (new_vals.get('awb_public_category_ids')[0][2] != [])) :
                product_int = new_vals.get('awb_public_category_ids')[0][2]
                #product_template = self.env['product.template'].search([('categ_id','in',product_int)])
                product_template = self.env['product.template'].search([('public_categ_ids','in',product_int)])
                for i in product_template: product_ids.append(i.id)
            else:
                if (vals.get('awb_product_selection_type') == 'category') or (new_vals.get('awb_product_selection_type') == 'category') or (self.awb_product_selection_type == 'category'):
                    for i in self.awb_public_category_ids.product_tmpl_ids: product_ids.append(i.id)
        
        elif (vals.get('awb_product_selection_type') == 'manual') or (new_vals.get('awb_product_selection_type') == 'manual'):
            if (vals.get('awb_product_rel_ids') and (vals.get('awb_product_rel_ids')[0][2] != [])):
                product_int = vals.get('awb_product_rel_ids')[0][2]
                product_template = self.env['product.template'].browse(product_int)
                for i in product_template: product_ids.append(i.id)
            elif (new_vals.get('awb_product_rel_ids') and (new_vals.get('awb_product_rel_ids')[0][2] != [])):
                product_int = new_vals.get('awb_product_rel_ids')[0][2]
                product_template = self.env['product.template'].browse(product_int)
                for i in product_template: product_ids.append(i.id)
            else:
                if (vals.get('awb_product_selection_type') == 'manual') or (new_vals.get('awb_product_selection_type') == 'manual') or (self.awb_product_selection_type == 'manual'):
                    for i in self.awb_product_rel_ids: product_ids.append(i.id)
        else:
            #updated the condition
            if (self.awb_product_selection_type == 'manual'):
                if (vals.get('awb_product_rel_ids') and (vals.get('awb_product_rel_ids')[0][2] != [])):
                    product_int = vals.get('awb_product_rel_ids')[0][2]
                    product_template = self.env['product.template'].browse(product_int)
                    for i in product_template: product_ids.append(i.id)
                elif (new_vals.get('awb_product_rel_ids') and (new_vals.get('awb_product_rel_ids')[0][2] != [])):
                    product_int = new_vals.get('awb_product_rel_ids')[0][2]
                    product_template = self.env['product.template'].browse(product_int)
                    for i in product_template: product_ids.append(i.id)
                else:
                    if (vals.get('awb_product_selection_type') == 'manual') or (new_vals.get('awb_product_selection_type') == 'manual') or (self.awb_product_selection_type == 'manual'):
                        for i in self.awb_product_rel_ids: product_ids.append(i.id)
            elif (self.awb_product_selection_type == 'category'):
                if (vals.get('awb_public_category_ids') and (vals.get('awb_public_category_ids')[0][2] != [])) :
                    product_int = vals.get('awb_public_category_ids')[0][2]
                    product_template = self.env['product.template'].search([('public_categ_ids','in',product_int)])
                    #product_template = self.env['product.template'].search([('categ_id','in',product_int)])
                    for i in product_template: product_ids.append(i.id)
                elif (new_vals.get('awb_public_category_ids') and (new_vals.get('awb_public_category_ids')[0][2] != [])) :
                    product_int = new_vals.get('awb_public_category_ids')[0][2]
                    #product_template = self.env['product.template'].search([('categ_id','in',product_int)])
                    product_template = self.env['product.template'].search([('public_categ_ids','in',product_int)])
                    for i in product_template: product_ids.append(i.id)
                else:
                    if (vals.get('awb_product_selection_type') == 'category') or (new_vals.get('awb_product_selection_type') == 'category') or (self.awb_product_selection_type == 'category'):
                        for i in self.awb_public_category_ids.product_tmpl_ids: product_ids.append(i.id)
        
        if content == 'facebook':
            ir_attachment = env['ir.attachment']
            create_date = datetime.now()
            xml_id = 'facebook_product_catelog.rss'
            context_copy = context.copy()
            if not context_copy.get('pricelist'):
                pricelist = vals.get('awb_pricelist_id') or new_vals.get('awb_pricelist_id') or self.awb_pricelist_id
                context_copy['pricelist'] = int(pricelist)
            else:
                pricelist = self.env['product.pricelist'].browse(
                    context_copy['pricelist'])
            products = self.env['product.template'].with_context(
                context_copy).sudo().search([
                    ('sale_ok', '=', True),
                    ('website_published', '=', True),
                    ('id','in',product_ids)
                ])
            
            if new_vals.get('website_id'):
                web_id = self.env['website'].search([('id','=',new_vals.get('website_id'))])
            elif  vals.get('website_id'):
                web_id = self.env['website'].search([('id','=',vals.get('website_id'))])
            else:
                web_id = self.website_id
                
            if new_vals.get('awb_currency_id'):
                res_cur = self.env['res.currency'].search([('id','=',new_vals.get('awb_currency_id'))])
            elif  vals.get('awb_currency_id'):
                res_cur = self.env['res.currency'].search([('id','=',vals.get('awb_currency_id'))])
            else:
                res_cur = self.awb_currency_id
            
            shop_url = vals.get('awb_shop_url') or new_vals.get('awb_shop_url') or self.awb_shop_url
            content = self.env.ref(xml_id)._render(
                dict(
                    products=products,
                    website = web_id,
                    url_root = shop_url,
                    currency_name = res_cur,
                    updated=create_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    ))
            # Replace to prevent error
            # XMLSyntaxError: Namespace prefix g on 'tag' is not defined
            content = str(content)
            #content = content.decode('utf-8')
            content = content.replace('__colon__', ':')
            content = content.replace('<f_link>', '<link>')
            content = content.replace('</f_link>', '</link>')
            message_bytes = content.encode('utf-8')
            base64_bytes = base64.b64encode(message_bytes)
            
            dir_path_demo = os.path.dirname(__file__)
            dir_path = dir_path_demo.split('models')
            if new_vals.get('name'):
                new_name = new_vals.get('name')
            else:
                new_name = ((self.name) or (vals.get('name')))
            
            path = dir_path[0] + 'static/src/xml/' + new_name + '.xml'
            #copying existing file
            #===================================================================
            # original = dir_path[0] + 'static/src/xml/dup.xml'
            # target = dir_path[0] + 'static/src/xml/' + new_name + '.xml'
            # shutil.copyfile(original, target)
            #===================================================================
            #changed path, updated new option, created file with x permission
           
            with open(path, 'wb') as myfile: 
                myfile.write(message_bytes)
            
            
            new_url = path.split('facebook_product_catelog') 
            shop_url = shop_url
            t = shop_url + '/facebook_product_catelog' + new_url[1] 
            attach_url = '/facebook_product_catelog' + new_url[1]
            #created attachment for the records. And returned url and Id of attachment.
            if self.id:
                ir_at = self.env['ir.attachment'].sudo().search([('res_id','=',self.id),('res_model','=','awb.fb.catalog')])
                irattachment = ir_at.sudo().write(dict(
                    datas=base64_bytes,
                    mimetype=FEED_MIMETYPE,
                    type='url',
                    name=new_name,
                    url=attach_url,
                    ))
            else:
                irattachment = ir_attachment.sudo().create(dict(
                    datas=base64_bytes,
                    mimetype=FEED_MIMETYPE,
                    type='url',
                    name=new_name,
                    url=attach_url,
                    ))
            datasupload = {}
            datasupload.update({'url':t,
                                'ir_attach':irattachment})
        return datasupload
    
    def _compute_product(self):
        #updating the attributes        
        items = self.env['awb.fb.catalog'].search([('id','=',self.id)])
        new_vals={}
        vals = {}
        for i in items:
            up = i.generate_feedfb(vals, new_vals)            
            i.update({'awb_feed_url':up.get('url')})
        self.awb_rel_name = 'exam'
    
    def cron_product_update(self):
        """product update method"""
        items = self.env['awb.fb.catalog'].search([])
        new_vals={}
        vals = {}
        for i in items:
            up = i.generate_feedfb(vals, new_vals)            
            i.update({'awb_feed_url':up.get('url')})
        