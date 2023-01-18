# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import io
import xlrd
import logging
import tempfile
import binascii
from datetime import date, datetime, time
from odoo import api, fields, models, tools, _
from odoo.exceptions import Warning, UserError, ValidationError
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    automation_stock_file = fields.Binary(related="company_id.automation_stock_file", string="Upload File", readonly=False)
    automation_stock_file_type = fields.Selection(related="company_id.automation_stock_file_type", string='File Type', default='XLS', readonly=False)

    @api.onchange("automation_stock_file")
    def onchange_automation_stock(self):
        if self.automation_stock_file:
            if self.automation_stock_file_type == 'XLS':
                try:
                    file = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                    file.write(binascii.a2b_base64(self.automation_stock_file))
                    file.seek(0)
                    values = {}
                    workbook = xlrd.open_workbook(file.name)
                    sheet = workbook.sheet_by_index(1)
                except Exception as e:
                    raise ValidationError(_("Please Select Valid File Format !, Error : "+str(e)))
    
                for row_no in range(sheet.nrows):
                    val = {}
                    if row_no <= 0:
                        fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
                    else:
                        line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                        if line[3]:
                            try:
                                if line[3] == 'group_stock_storage_categories' and line[5] == 'Yes' and not self.group_stock_multi_locations:
                                    self[line[5]] = False
                                    continue
                                
                                if line[3] == 'default_picking_policy':
                                    if line[5] == 'Yes':
                                        self[line[3]] = line[4] or 'direct'
                                    elif not self.default_picking_policy:
                                        self.default_picking_policy = 'direct'
                                    continue
                                
                                if line[3] == 'annual_inventory_day' and line[5] == 'Yes':
                                    if line[4]:
                                        temp = str(line[4]).split('-')
                                        self.annual_inventory_day = int(temp[0])
                                        self.annual_inventory_month = str(int(temp[1]))
                                    continue
                                
                                if line[3] == 'security_lead' and line[5] == 'Yes':
                                    self.use_security_lead = True
                                    self.security_lead = float(line[4] or 0)
                                    continue
                                else:
                                    self.use_security_lead = False
                                    
                                if line[3] == 'po_lead' and line[5] == 'Yes':
                                    self.use_po_lead = True
                                    self.po_lead = float(line[4] or 0)
                                else:
                                    self.use_po_lead = False
                                
                                if line[3] == 'days_to_purchase' and line[5] == 'Yes':
                                    self.days_to_purchase = float(line[4] or 0)
                                    
                                if line[5] == 'Yes':
                                    self[line[3]] = True
                                else:
                                    self[line[3]] = False
                            except Exception as e:
                                print(e)
                        
                            
    def auto_import_stock(self):
        if self.automation_stock_file:
            if self.automation_stock_file_type == 'XLS':
                try:
                    file = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                    file.write(binascii.a2b_base64(self.automation_stock_file))
                    file.seek(0)
                    workbook = xlrd.open_workbook(file.name)
                    #inventory Warehouse
                    wh_sheet = workbook.sheet_by_index(2)
                    self.import_warehouse(wh_sheet)
                    #inventory Locations
                    location_sheet = workbook.sheet_by_index(3)
                    self.import_warehouse_locations(location_sheet)
                    #inventory Product Category
                    category_sheet = workbook.sheet_by_index(4)
                    self.import_stock_category(category_sheet)
                    #inventory Product UOM
                    uom_sheet = workbook.sheet_by_index(5)
                    self.import_stock_uom(uom_sheet)
                    #inventory Product Attributes
                    product_attrbute_sheet = workbook.sheet_by_index(6)
                    self.import_stock_product_attribute(product_attrbute_sheet)
                    #inventory Customer or Vendor
                    partner_sheet = workbook.sheet_by_index(8)
                    self.import_partner(partner_sheet)
                    #inventory Product
                    product_sheet = workbook.sheet_by_index(7)
                    self.import_stock_product(product_sheet)
                    
                    message = 'All Records imported successfully'
                    classname = 'bg-success'
                    tip_type = 'success'
                    notification = {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': u'Import results',
                            'message': message,
                            'sticky': True,
                            'type': tip_type,
                            'className': classname,
                            'next': {
                                'type': 'ir.actions.act_window_close'
                            },
                        },
                    }
                    return notification
                    

                except Exception as e:
                    print(e)
                    raise ValidationError(_("Please Select Valid File Format !  or "+str(e)))
                
    def import_partner(self, sheet):
        for row_no in range(sheet.nrows):
            val = {}; parent_id = country_id = state_id = False
            if row_no <= 0:
                fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
            else:
                line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                partner_id = self.env['res.partner'].search(['|',('id','=',int(float(line[2] or 0))), ('import_id','=', line[1] or 'No ID')], limit=1)
                if (line[7] or line[6] or line[8]) and not partner_id:
                    partner_id = self.env['res.partner'].search(['|','|',('email','=', line[6] or 'no email'), ('mobile','=', line[7]), ('phone','=', line[8])], limit=1)
                
                if line[14]:
                    country_id = self.env['res.country'].search(['|',('name','=', line[14]), ('code','=', line[14])], limit=1)
                    if country_id and line[13]:
                        state_id = self.env['res.country.state'].search(['|',('name','=', line[13]), ('code','=', line[13]), ('country_id','=',country_id.id)], limit=1)
                
                val.update( {
                    'name':line[4],
                    'import_id':line[1],
                    'company_type': line[5] == 'Company' and 'company' or 'person',
                    'supplier_rank': line[9] == 'Vendor' and 1 or False,
                    'customer_rank': line[9] == 'Customer' and 1 or False,
                    'email':line[6],
                    'mobile':line[7],
                    'phone':line[8],
                    'street':line[10],
                    'street2':line[11],
                    'city':line[12],
                    'zip':str(line[15]),
                    'country_id':country_id and country_id.id or False,
                    'state_id':state_id and state_id.id or False,
                    })
                
                if not partner_id:
                    partner_id = self.env['res.partner'].create(val)
                elif line[3] == "Yes":
                    if not line[4]:
                         val.update({
                             'name': partner_id.name,
                             })
                    partner_id.write(val)
                            
    def import_warehouse(self, sheet):
            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
                else:
                    line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                    wh_id = self.env['stock.warehouse'].search([('code','=',line[2]),'|', ('active','=',True), ('active','=',False)])
                    partner_id = False
                    if line[3]:
                        partner_id = int(float(line[3]))
                    val.update( {
                        'name':line[1],
                        'partner_id': partner_id,
                        'company_id': int(float(line[4] or self.env.company.id)),
                        })
                    if not wh_id:
                        val.update({'code': line[2]})
                        res = self.env['stock.warehouse'].create(val)
                    elif line[5] == "Yes":
                        val.update({'active': True})
                        wh_id.write(val)
                        
                        
    def import_warehouse_locations(self, sheet):
        for row_no in range(sheet.nrows):
            val = {}; parent_id = False
            if row_no <= 0:
                fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
            else:
                line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                wh_id = self.env['stock.warehouse'].search([('code','=',line[5]),'|', ('active','=',True), ('active','=',False)])
                if wh_id:
                    location_id = self.env['stock.location'].search(['|',('id','=',int(float(line[2] or 0))), ('import_id','=', line[1])], limit=1)
                    if line[7] or line[6]:
                        parent_id = self.env['stock.location'].search(['|',('id','=',int(float(line[7] or 0))), ('import_id','=', line[6])], limit=1)
                    if line[8] and not parent_id:
                        parent_ids = self.env['stock.location'].search([('warehouse_id','=',wh_id.id)])
                        parent_ids = parent_ids.filtered(lambda rec:rec.warehouse_id.id == wh_id.id and rec.display_name == line[8])
                        if parent_ids:
                            parent_id = parent_ids[0]
                                
                    if not parent_id:
                        parent_id = wh_id.lot_stock_id
                    val.update( {
                        'name':line[4],
                        'import_id':line[1],
                        'location_id': parent_id and parent_id.id or False,
                        'scrap_location': line[10] == 'Yes' and True or False,
                        'return_location': line[11] == 'Yes' and True or False,
                        'usage' : self.get_location_type(str(line[9]))
                        })
                    if not location_id:
                        res = self.env['stock.location'].create(val)
                    elif line[3] == "Yes":
                        location_id.write(val)
                        
    def get_account_idbycode(self, code):
        account_id = self.env['account.account'].search([('code','=',code)], limit=1)
        if account_id:
            return account_id.id
        else:
            return False
                        
    def import_stock_category(self, sheet):
        for row_no in range(sheet.nrows):
            val = {}; parent_id = False;removal_strategy_id = False; cost_method = 'standard'; valuation = 'manual_periodic'
            val_account_id = val_journal_id = val_input_account_id = val_output_account_id = False;
            if row_no <= 0:
                fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
            else:
                line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                if line[2] or line[1]:
                    categ_id = self.env['product.category'].search(['|',('id','=',int(float(line[2] or 0))), ('import_id','=', line[1])], limit=1)
                    if line[5] or line[6]:
                        parent_id = self.env['product.category'].search(['|',('id','=',int(float(line[5] or 0))), ('import_id','=', line[6])], limit=1)
                        # if not parent_id and line[4]:
                        #     parent_ids = self.env['product.category'].search([])
                        #     parent_ids = parent_ids.filtered(lambda rec:rec.display_name == line[4])
                        #     if parent_ids:
                        #         parent_id = parent_ids[0]
                        
                    if line[7] and line[7] == "FIFO":
                        removal_strategy_id = "fifo"
                    elif line[7] and line[7] == "LIFO":
                        removal_strategy_id = "lifo"
                    elif line[7] and line[7] == "CL":
                        removal_strategy_id = "closest"
                        
                    if removal_strategy_id:
                        removal_strategy_id = self.env['product.removal'].search([('method','=',removal_strategy_id)], limit=1)
                        
                    if line[8] and line[8] == "FIFO":
                        cost_method = "fifo"
                    elif line[8] and line[8] == "Average cost":
                        cost_method = "average"
                    else:
                        cost_method = "standard"
                        
                    if line[9] and line[9] == "Manual":
                        valuation = "manual_periodic"
                    elif line[9] and line[9] == "Automated":
                        valuation = "real_time"
                        val_account_id = self.get_account_idbycode(line[10])
                        val_input_account_id = self.get_account_idbycode(line[12])
                        val_output_account_id = self.get_account_idbycode(line[13])
                        val_journal_id = self.env['account.journal'].search([('code','=',line[11])], limit=1)
                        if val_journal_id:
                            val.update({'property_stock_journal':val_journal_id.id})
                        if (not val_account_id) or (not val_input_account_id) or (not val_output_account_id):
                            valuation = "manual_periodic"
                            
                    
                    val.update( {
                        'import_id':line[1],
                        'name':line[4],
                        'parent_id': parent_id and parent_id.id or False,
                        'removal_strategy_id': removal_strategy_id and removal_strategy_id.id or False,
                        'property_cost_method': cost_method,
                        'property_valuation' : valuation,
                        'property_stock_valuation_account_id' : val_account_id,
                        'property_stock_account_input_categ_id' : val_input_account_id,
                        'property_stock_account_output_categ_id' : val_output_account_id,
                        })
                    if not categ_id:
                        res = self.env['product.category'].create(val)
                    elif line[3] == "Yes":
                        if not line[4]:
                            val.update({'name':categ_id.name})
                        categ_id.write(val)
                        
    def import_stock_uom(self, sheet):
        for row_no in range(sheet.nrows):
            val = {}; parent_id = False; ratio = 0.01; round_pre = 0.01; active = True ; type = ''
            if row_no <= 0:
                fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
            else:
                line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                if line[2] or line[1]:
                    uom_id = self.env['uom.uom'].search(['|',('id','=',int(float(line[2] or 0))), ('import_id','=', line[1])], limit=1)
                    if line[5] or line[6]:
                        uom_categ_id = self.env['uom.category'].search([('id','=',int(float(line[5] or 0)))], limit=1)
                        if not uom_categ_id and line[6]:
                            uom_categ_id = self.env['uom.category'].search([('name','=', line[6])], limit=1)
                    
                    if (float(line[8])) > 0:
                        ratio = float(line[8])
                    if (float(line[9])) > 0:
                        round_pre = float(line[9])
                    if line[9] and line[7] == "No":
                        active = False
                    
                    if line[10] and line[10] == "Bigger":
                        type = "bigger"
                    elif line[10] and line[10] == "Reference":
                        type = "reference"
                    elif line[10] and line[10] == "Smaller":
                        type = "smaller"
                    
                    
                    val.update( {
                        'import_id':line[1],
                        'name':line[4],
                        'category_id': uom_categ_id and uom_categ_id.id or False,
                        # 'factor': ratio,
                        'rounding' : round_pre,
                        'active' : active,
                        'uom_type' : type,
                        })
                    
                    if not uom_id:
                        res = self.env['uom.uom'].create(val)
                        # uom_categ_id.write({"uom_ids":[(0,0, val)]})
                        if ratio:
                            try:
                                res.write({'factor':ratio})
                            except Exception as e:
                                _logger.info(str(e))
                                pass
                    elif line[3] == 'Yes':
                        if not line[4]:
                            val.update({'name':uom_id.name})
                            
                        uom_id.write(val)
                            
                        if ratio:
                            try:
                                res.write({'factor':ratio})
                            except Exception as e:
                                _logger.info(str(e))
                                pass


    def import_stock_product_attribute(self, sheet):
        update = False
        for row_no in range(sheet.nrows):
            val = {}; uom_id = False; ratio = 0.01; round_pre = 0.01; active = True ; type = ''
            if row_no <= 0:
                fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
            else:
                line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                if line[2] or line[1] or line[11] or line[12]:
                    product_attr_id = self.env['product.attribute'].search(['|',('id','=',int(float(line[2] or 0))), ('import_id','=', line[1])], limit=1)
                    if (not product_attr_id) and (line[11] or line[12]):
                        product_attr_id = self.env['product.attribute'].search(['|',('id','=',int(float(line[12] or 0))), ('import_id','=', line[11])], limit=1)
                        
                    if not product_attr_id and (line[4] or line[13]):
                        product_attr_id = self.env['product.attribute'].search(['|',('name','=',line[4]), ('name','=',line[13])], limit=1)
                            
                    val.update( {
                        'import_id':line[1] or product_attr_id and product_attr_id.import_id,
                        'name':line[4] or product_attr_id and product_attr_id.name,
                        'display_type': line[5] or product_attr_id and product_attr_id.display_type,
                        'create_variant': line[6] or product_attr_id and product_attr_id.create_variant,
                        })
                    
                    if not product_attr_id:
                        update = True
                        if line[1] or line[4]:
                            product_attr_id = self.env['product.attribute'].create(val)
                        if line[7]:
                            attr_val_id = self.env['product.attribute.value'].search([('name','=',line[7]), ('attribute_id','=',product_attr_id.id)], limit=1)
                            if line[9] == 'Yes' and not attr_val_id:
                                self.env['product.attribute.value'].create({'attribute_id':product_attr_id.id,'name':line[7],'html_color':line[8]})
                            elif line[10] == 'Yes' and attr_val_id:
                                attr_val_id.unlink()
                    
                    else:
                        if line[3] == "Yes" or update:
                            update = True
                            if line[4]: 
                                if not line[4]:
                                    val.update({'name':product_attr_id.name})
                                product_attr_id.write(val)  
                                    
                            if line[7]:
                                attr_val_id = self.env['product.attribute.value'].search([('name','=',line[7]), ('attribute_id','=',product_attr_id.id)], limit=1)
                                if line[9] == 'Yes' and not attr_val_id:
                                    self.env['product.attribute.value'].create({'attribute_id':product_attr_id.id,'name':line[7],'html_color':line[8]})
                                elif line[10] == 'Yes' and attr_val_id:
                                    attr_val_id.unlink()      
                        else:
                            update = False                

                            
                            
    def import_stock_product(self, sheet):
        pre_product_id = update = categ_id = False
        for row_no in range(sheet.nrows):
            val = {}; uom_id = False; ratio = 0.01; round_pre = 0.01; active = True ; type = '';
            if row_no <= 0:
                fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
            else:
                line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                if line[2] or line[1] or line[18] or line[19] or line[5]:
                    product_id = self.env['product.template'].search(['|',('id','=',int(float(line[2] or 0))), ('import_id','=', line[1])], limit=1)
                    if not product_id:
                        product_id = self.env['product.template'].search(['|',('id','=',int(float(line[19] or 0))), ('import_id','=', line[18])], limit=1)
                    if not product_id and line[5]:
                        product_id = self.env['product.template'].search([('default_code','=', line[5])], limit=1)
                    if line[7]:
                        uom_id = self.env['uom.uom'].search([('id','=',int(float(line[7] or 0)))], limit=1)
                    if not uom_id and line[6]:
                        uom_id = self.env['uom.uom'].search([('name','=', line[6])], limit=1)
                    # if line[8] == "All / Saleable / Filters":
                    #     pass
                    categ_id = False
                    if line[9]:
                        categ_id = self.env['product.category'].search([('id','=',int(float(line[9] or 0)))], limit=1)
                    if not categ_id and line[8]:
                        categ_ids = self.env['product.category'].search([])
                        categ_ids = categ_ids.filtered(lambda rec:rec.display_name == line[8])
                        if categ_ids:
                            categ_id = categ_ids[0]
                            
                    if line[35]:
                        vendor_uom_id = self.env['uom.uom'].search([('name','=', line[35])], limit=1)
                        if vendor_uom_id:
                            val.update({"uom_po_id":vendor_uom_id.id})
                            
                    if line[37]:
                        if line[37] == "On ordered quantities":
                            val.update({"purchase_method":"purchase"})
                        elif line[37] == "On received quantities":
                            val.update({"purchase_method":"receive"})
                    

                    if line[4] or line[5]:
                        val.update( {
                            'name':line[4] or product_id and product_id.name,
                            'import_id':line[1] or product_id and product_id.import_id,
                            'categ_id': categ_id and categ_id.id or product_id and product_id.categ_id.id or False,
                            'default_code': line[5] or product_id and product_id.default_code,
                            'uom_id' : uom_id and uom_id.id or product_id and product_id.uom_id.id or False,
                            'detailed_type' : line[10]=='Storable Product' and 'product' or line[10]=='Consumable' and 'consu' or 'service',
                            'invoice_policy': line[11] or product_id and product_id.invoice_policy,
                            'list_price': line[12] or product_id and product_id.list_price,
                            'standard_price': line[13] or product_id and product_id.standard_price,
                            'sale_ok': line[31] in ['True', '1', '1.0'] and True or False,
                            'purchase_ok': line[32] in ['True', '1', '1.0'] and True or False,
                            'barcode': line[33] or False,
                            })
                    
                    if not product_id:
                        update = True
                        product_id = self.env['product.template'].create(val)
                        pre_product_id = product_id
                        if line[14]:
                            attr_id = self.env['product.attribute'].search([('name','=',line[14])], limit=1)
                            if attr_id:
                                product_attr_id = product_id.attribute_line_ids.filtered(lambda rec:rec.attribute_id.id == attr_id.id)
                                if product_attr_id:
                                    product_attr_id = product_attr_id[0]
                                if line[15] and product_attr_id:
                                    attr_line_ids = self.env['product.attribute.value'].search([('attribute_id','=',attr_id.id),('name','in',str(line[15]).split(','))])
                                    product_attr_id.value_ids = product_attr_id.value_ids.ids + attr_line_ids.ids
                                elif line[15] and not product_attr_id:
                                    attr_line_ids = self.env['product.attribute.value'].search([('attribute_id','=',attr_id.id), ('name','in',str(line[15]).split(','))])
                                    product_attr_id = self.env['product.template.attribute.line'].create({'attribute_id':attr_id.id,'value_ids':attr_line_ids.ids, 'product_tmpl_id':product_id.id})
                            
                        
                    else:
                        if line[3] == "Yes" or update:
                            update = True
                            if not line[4]:
                                val.update({'name':product_id.name})
                            product_id.write(val)
                            
                            if line[14]:
                                attr_id = self.env['product.attribute'].search([('name','=',line[14])], limit=1)
                                if attr_id:
                                    product_attr_id = product_id.attribute_line_ids.filtered(lambda rec:rec.attribute_id.id == attr_id.id)
                                    if product_attr_id:
                                        product_attr_id = product_attr_id[0]
                                    if line[15] and product_attr_id:
                                        attr_line_ids = self.env['product.attribute.value'].search([('name','in',str(line[15]).split(','))])
                                        product_attr_id.value_ids = product_attr_id.value_ids.ids + attr_line_ids.ids
                                    elif line[15] and not product_attr_id:
                                        attr_line_ids = self.env['product.attribute.value'].search([('attribute_id','=',attr_id.id), ('name','in',str(line[15]).split(','))])
                                        product_attr_id = self.env['product.template.attribute.line'].create({'attribute_id':attr_id.id,'value_ids':attr_line_ids.ids, 'product_tmpl_id':product_id.id})
                                    
                                    if line[16] and product_attr_id:
                                        attr_line_ids = self.env['product.attribute.value'].search([('attribute_id','=',attr_id.id), ('name','in',str(line[16]).split(','))])
                                        value_ids = list(set(product_attr_id.value_ids.ids).difference(set(attr_line_ids.ids)))
                                        if not value_ids:
                                            product_attr_id.unlink()
                                        else:
                                            for attr_line_id in attr_line_ids:
                                                product_attr_id.value_ids = [(3,attr_line_id.id)]
                        else:
                            update = False
                            
                            
                    if update and product_id and (line[22] or line[23] or line[24]):
                        vendor_val = {}; seller_val = {}
                        vendor_id = self.env['res.partner'].search(['|','|',('email','=',line[22] or 'no email'), ('mobile','=', line[23] or 'no mobile'), ('phone','=',line[24] or 'no phone')], limit=1)
                        vendor_val.update( {
                            'name':line[21] or line[22],
                            'company_type': 'company',
                            'supplier_rank': 1,
                            'email':line[22],
                            'mobile':line[23],
                            'phone':line[24],
                            })
                        if not vendor_id:
                            vendor_id = self.env['res.partner'].create(vendor_val)
                        seller_id = self.env['product.supplierinfo'].search([('name','=',vendor_id.id), ('product_tmpl_id','=',product_id.id)], limit=1)
                        if line[28]:
                            vendor_uom_id = self.env['uom.uom'].search([('id','=',int(float(line[28] or 0)))], limit=1)
                        if not vendor_uom_id and line[27]:
                            vendor_uom_id = self.env['uom.uom'].search([('name','=', line[27])], limit=1)
                        
                        seller_val.update( {
                            'name':vendor_id.id,
                            'product_code': line[25],
                            'price': line[29],
                            'min_qty': line[26] or 1,
                            'delay':int(float(line[30] or 0)),
                            'product_uom':vendor_uom_id and vendor_uom_id.id or 1,
                            'product_tmpl_id':product_id.id,
                            })
                        if not seller_id:
                            seller_id = self.env['product.supplierinfo'].create(seller_val)
                        else:
                            seller_id.write(seller_val)
                        
                        
                        
                            
                        
                        
                            
                        
    def get_location_type(self, type):
        if type == "Vendor Location":
            return "supplier"
        elif type == "View":
            return "view"
        elif type == "Internal Location":
            return "internal"
        elif type == "Customer Location":
            return "customer"
        elif type == "Inventory Loss":
            return "inventory"
        elif type == "Production":
            return "production"
        elif type == "Transit Location":
            return "transit"
        else:
            return "internal"
                    
                        
    

        
        
        
        
        
        