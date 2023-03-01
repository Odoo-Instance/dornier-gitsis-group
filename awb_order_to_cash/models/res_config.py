# -*- coding: utf-8 -*-
"""imports from python lib"""
import binascii
import base64 # @UnusedImport
from datetime import datetime
import os  # @UnusedImport
import shutil # @UnusedImport
import tempfile  # @UnusedImport
import xlrd


"""imports from odoo"""
from odoo import fields, models, api, _  # @UnusedImport
from odoo.http import request
from odoo.exceptions import ValidationError






"""inherited res.config.settings model for adding fields"""
class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = "adding custom fields"

    awb_automation_sale_file = fields.Binary(related="company_id.awb_automation_sale_file", string="Upload File", readonly=False)
    awb_automation_sale_file_type = fields.Selection(related="company_id.awb_automation_sale_file_type", string='File Type', default='xls', readonly=False)
    account_credit_limit = fields.Boolean(
        string="Sales Credit Limit", related="company_id.account_credit_limit", readonly=False,
        help="Enable credit limit for the current company.")
    account_default_credit_limit = fields.Monetary(
        string="Default Credit Limit", related="company_id.account_default_credit_limit", readonly=False,
        help="A limit of zero means no limit by default.")
    credit_limit_type = fields.Selection(string="Credit Limit Type", related="company_id.credit_limit_type",
                                         readonly=False)
    is_delivery_set_to_done_awb = fields.Boolean(string="Is Delivery Set to Done")
    create_invoice_awb =fields.Boolean(string='Create Invoice?')
    validate_invoice_awb = fields.Boolean(string='Validate invoice?')
    confirm_sale_awb = fields.Boolean(string='Confirm Sale Order')
    
    @api.model
    def set_values(self):
        """Set value to ir.config_parameter"""
        res = super(ResConfigSettingsInherit, self).set_values()
        self.env['ir.config_parameter'].set_param('is_delivery_set_to_done', self.is_delivery_set_to_done_awb)
        self.env['ir.config_parameter'].set_param('create_invoice', self.create_invoice_awb)
        self.env['ir.config_parameter'].set_param('validate_invoice', self.validate_invoice_awb)
        self.env['ir.config_parameter'].set_param('confirm_sale', self.confirm_sale_awb)
        return res
 
    @api.model
    def get_values(self):
        """get value from ir.config_parameter"""
        res = super(ResConfigSettingsInherit, self).get_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        is_delivery_set_to_done_db = IrConfigParameter.get_param('is_delivery_set_to_done')
        create_invoice_db = IrConfigParameter.get_param('create_invoice')
        validate_invoice_db = IrConfigParameter.get_param('validate_invoice')
        confirm_sale_db = IrConfigParameter.get_param('confirm_sale')
        res.update(
            is_delivery_set_to_done_awb = is_delivery_set_to_done_db,
            create_invoice_awb = create_invoice_db,
            validate_invoice_awb = validate_invoice_db,
            confirm_sale_awb = confirm_sale_db
        )
        return res
    
    
    #to import orders.
    def auto_import_order(self):
        """"Convert the file into binary and saved in filestore. Each and every time it will convert the data from io."""
        if self.awb_automation_sale_file:
            if self.awb_automation_sale_file_type == 'xls':
                try:
                    request.session['import_sale_order'] = set()
                    request.session['awb_sale_order'] = False
                    myfile = tempfile.NamedTemporaryFile(delete= False,suffix=".xls")
                    myfile.write(binascii.a2b_base64(self.awb_automation_sale_file))
                    myfile.seek(0)
                    workbook = xlrd.open_workbook(myfile.name)
                    #partner_sheet_names = workbook.sheet_names()
                    
                    partner_sheet = workbook.sheet_by_index(0)
                    sale_order_sheet = workbook.sheet_by_index(1)
                    self.import_res_partner(partner_sheet)
                    self.import_sale_partner(sale_order_sheet)
                    
                    #Added success message notification
                    message = 'All Records imported successfully'
                    class_name = 'bg-success'
                    msg_type = 'success'
                    notification = {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': u'Import results',
                            'message': message,
                            'sticky': True,
                            'type': msg_type,
                            'className': class_name,
                            'next': {
                                'type': 'ir.actions.act_window_close'
                            },
                        },
                    }
                    return notification

                except Exception as e:
                    raise ValidationError(_(str(e)))
          
           
            
    
    def import_res_partner(self, sheet):
        """Create a res.partner record from template"""
        for row_no in range(sheet.nrows):
            val = {};  country_id = state_id = False
            if row_no <= 0:
                fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
            else:
                line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                if (line[2] or line[1] or line[7]):
                    partner_id = self.env['res.partner'].search([('email','=', line[2]), ('name','=', line[0])], limit=1)
                if line[4]:
                    country_id = self.env['res.country'].search(['|',('name','=', line[5]), ('code','=', line[5])], limit=1)
                    if country_id and line[5]:
                        if line[5]:
                            s_name = line[4].strip()
                            state_id = self.env['res.country.state'].sudo().search([('country_id','=',country_id.id),('name','=', s_name)])
                        else:
                            state_id = self.env['res.country.state'].sudo().search([('code','=', line[4]), ('country_id','=',country_id.id)])
                if not partner_id:
                    val.update({
                        'name':line[0],
                        'company_type': 'company' if line[12] == 'Company' else 'person',
                        #'supplier_rank': line[9] == 'Vendor' and 1 or False,
                        #'customer_rank': line[9] == 'Customer' and 1 or False,
                        'email':line[2],
                        'mobile':int(float(line[7])) if len(line[7]) > 0 else line[7],
                        'phone':int(float(line[1])) if len(line[1]) > 0 else line[1],
                        'street':line[8],
                        'street2':line[9],
                        'city':line[3],
                        'zip':int(float(line[10])) if len(line[10]) > 0 else line[10],
                        'country_id':country_id and country_id.id or False,
                        'state_id':state_id and state_id.id or False,
                        'is_company': True if line[13] == 'Yes' else False,
                        'awb_customer_category': 'd2c' if line[11] == 'Direct to Consumer' else 'b2b',
                        'awb_tin': line[16]
                        })
                    if val.get('company_type') == 'person':
                        if line[20] == 'Contact':
                            a_type = 'contact'
                        elif line[20] == 'Invoice Address':
                            a_type = 'invoice'
                        elif line[20] == 'Delivery Address':
                            a_type = 'delivery'
                        elif line[20] == 'Other Address':
                            a_type = 'other'
                        elif line[20] == 'Private Address':
                            a_type = 'private'
                        val.update({'type':a_type})

                if not partner_id:
                    partner_id = self.env['res.partner'].create(val)
                    if (line[17] or line[18] or line[19]):
                        c_name = line[18].strip()
                        contact_partner = self.env['res.partner'].search(['|',('email','=', line[17]),  ('name','=', c_name)], limit=1)
                        if not contact_partner:
                            c_vals = {};
                            c_vals.update({'name': line[18],
                                           'email': line[17],
                                           'mobile':int(float(line[19])) if len(line[19]) > 0 else line[19]})
                            contact_partner_id = self.env['res.partner'].create(c_vals)
                            partner_id.child_ids = [(6,0,[contact_partner_id.id])]
                        else:
                            partner_id.child_ids = [(6,0,[contact_partner.id])]
                
                elif line[21] == 'Yes':
                    val.update({
                        'name':line[0],
                        'company_type': 'company' if line[12] == 'Company' else 'person',
                        #'supplier_rank': line[9] == 'Vendor' and 1 or False,
                        #'customer_rank': line[9] == 'Customer' and 1 or False,
                        'email':line[2],
                        'mobile':int(float(line[7])) if len(line[7]) > 0 else line[7],
                        'phone':int(float(line[1])) if len(line[1]) > 0 else line[1],
                        'street':line[8],
                        'street2':line[9],
                        'city':line[3],
                        'zip':int(float(line[10])) if len(line[10]) > 0 else line[10],
                        'country_id':country_id and country_id.id or False,
                        'state_id':state_id and state_id.id or False,
                        'is_company': True if line[13] == 'Yes' else False,
                        'awb_customer_category': 'd2c' if line[11] == 'Direct to Consumer' else 'b2b',
                        'awb_tin': line[16]
                        })
                    new_val = {}
                    for k,v in val.items():
                        if len(str(v))>0:
                            if str(v) != 'False':
                                new_val.update({k:v})
                    partner_id.write(new_val)
                
                elif (line[17] or line[18] or line[19]):
                    c_name = line[18].strip()
                    contact_partner = self.env['res.partner'].search(['|',('email','=', line[17]), ('name','=', c_name)], limit=1)
                    if not contact_partner:
                        c_vals = {};
                        c_vals.update({'name': line[18],
                                       'email': line[17],
                                       'mobile':int(float(line[19])) if len(line[19]) > 0 else line[19]})
                        contact_partner_id = self.env['res.partner'].create(c_vals)
                        exist_ids = partner_id.child_ids.ids or partner_id.child_ids.id
                        partner_id.child_ids = [(6,0,[contact_partner_id.id, exist_ids])]
                    else:
                        exist_ids = partner_id.child_ids.ids or partner_id.child_ids.id
                        if len(exist_ids) > 0:
                            exist_ids.extend([contact_partner.id])
                            partner_id.child_ids = [(6,0,exist_ids)]
                        else:
                            partner_id.child_ids = [(6,0,[contact_partner.id])]
    
    def import_sale_partner(self, sheet):                   
        """Creating sale order record."""
        request.session['import_sale_order'] = set()
        request.session['confirm_sale_order'] = []
        for row_no in range(sheet.nrows):
            val = {};  
            if row_no <= 0:
                fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
                request.session['import_sale_order'] = set()
            else:
                line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                partner = self.env['res.partner'].search([('name','=',line[2])], limit=1)
                invoice_address  = self.env['res.partner'].search([('name','=',line[6])], limit=1)
                delivery_address  = self.env['res.partner'].search([('name','=',line[7])], limit=1)
                sale_person = self.env['res.users'].search([('name','=',line[3])], limit=1)
                sale_team = self.env['crm.team'].search([('name','=',line[5])], limit=1)
                product = self.env['product.product'].search([('name','=',line[10])], limit=1)
                company = self.env['res.company'].search([('name','=',line[4])])
                payment_terms = self.env['account.payment.term'].search([('name','=',line[14])])
                pricelist_id = self.env['product.pricelist'].search([('name','=',line[15])], limit=1)
                tax_ar = []
                if line[16]:
                    tax_id = (line[16]).split(',')
                    for i in tax_id:
                        t = i.strip()
                        tax = self.env['account.tax'].search([('name','=',t),('type_tax_use','=','sale')], limit=1)
                        tax_ar.append(tax.id)
                
                if line[1]:
                    date = float(line[1])
                    awb_date = (int(date) - 25569) * 24 * 60 * 60 * 1000
                    my_datetime = datetime.fromtimestamp(awb_date / 1000)
                if line[13] == 'Yes':
                    ex_sale = self.env['sale.order'].search(['|',('name','=',line[0]),('import_id_awb','=',line[17])],limit=1)
                    val = {}
                    if ex_sale.payment_term_id:
                        prev_payment = ex_sale.payment_term_id.id
                    else:
                        prev_payment = False
                    #changed the update functions
                    if ex_sale.state in ['sent', 'draft']:
                        if (line[9] == '1'):
                            req_sig = True
                        elif (line[9] == '0'):
                            req_sig = False
                        else:
                            req_sig = ex_sale.require_signature
                        if (line[8] == '1'):
                            req_pay = True
                        elif (line[8] == '0'):
                            req_pay = False
                        else:
                            req_pay = ex_sale.require_signature
                        val.update({'name': line[0] or ex_sale.name,
                                       'date_order': my_datetime or ex_sale.date_order,
                                       'partner_id': partner.id or ex_sale.partner_id.id,
                                      'partner_invoice_id': invoice_address.id if invoice_address else ex_sale.partner_invoice_id.id, 
                                      'partner_shipping_id': delivery_address.id if delivery_address else ex_sale.partner_shipping_id.id,
                                      'user_id': sale_person.id if sale_person else ex_sale.user_id.id,
                                      'team_id': sale_team.id if sale_team else ex_sale.team_id.id,
                                      #'company_id': company.id if company else ex_sale.comapny_id.id,
                                      'payment_term_id': payment_terms.id if payment_terms else prev_payment,
                                      'require_signature': req_sig,
                                       'require_payment': req_pay,
                                      # 'pricelist_id': pricelist_id.id if pricelist_id else ex_sale.pricelist_id.id,
                                    })
                        if pricelist_id:
                            ex_sale.pricelist_id = pricelist_id.id
                        if company:
                            ex_sale.company_id = company.id
                        ex_sale.write(val)
                        if (line[10] and ex_sale):
                            order_line = self.env['sale.order.line'].create({'product_id':product.id,
                                                                             'product_uom_qty':float(line[11]),
                                                                             'price_unit': float(line[12]),
                                                                             'name': product.name,
                                                                             'order_id': ex_sale.id})
                        request.session['import_sale_order'].add(ex_sale.id)
                        request.session['confirm_sale_order'].append(ex_sale.id)
                    else:
                        val.update({
                                  'partner_invoice_id': invoice_address.id if invoice_address else ex_sale.partner_invoice_id.id, 
                                  'partner_shipping_id': delivery_address.id if delivery_address else ex_sale.partner_shipping_id.id,
                                  'user_id': sale_person.id if sale_person else ex_sale.user_id.id,
                                  'team_id': sale_team.id if sale_team else ex_sale.team_id.id,
                                  'company_id': company.id if company else ex_sale.comapny_id.id,
                                  'payment_term_id': payment_terms.id if payment_terms else prev_payment,
                                })
                        ex_sale.write(val)
                        if (line[10] and ex_sale):
                            order_line = self.env['sale.order.line'].create({'product_id':product.id,
                                                                             'product_uom_qty':float(line[11]),
                                                                             'price_unit': float(line[12]),
                                                                             'name': product.name,
                                                                             'order_id': ex_sale.id})
                            
                        #ex_sale.order_line = [(5,0,[order_line.id])]
                elif (line[13] == 'No') or (line[13] == ''):
                    if partner:
                        ex_sale = self.env['sale.order'].search(['|',('name','=',line[0]),('import_id_awb','=',line[17])], limit=1)
                        if ex_sale:
                            request.session['import_sale_order'].add(ex_sale.id)
                            request.session['confirm_sale_order'].append(ex_sale.id)
                            continue
                        else:
                            sale = self.env['sale.order'].create({'name': line[0],
                                                              'date_order': my_datetime,
                                                              'partner_id': partner.id,
                                                              'partner_invoice_id': invoice_address.id if invoice_address else partner.id, 
                                                              'partner_shipping_id': delivery_address.id if delivery_address else partner.id,
                                                              'user_id': sale_person.id if sale_person else False,
                                                              'team_id': sale_team.id if sale_team else False,
                                                              #'company_id': company.id if company else self.env.user.company_id.id,
                                                              'require_signature': True if(line[9] == '1') else False,
                                                              'require_payment': True if(line[8] == '1') else False,
                                                              'import_id_awb':line[17],
                                                              'payment_term_id': payment_terms.id if payment_terms else '',
                                                              #'pricelist_id': pricelist_id.id if pricelist_id else '',
                            })
                            order_line = self.env['sale.order.line'].create({'product_id':product.id,
                                                                         'product_uom_qty':float(line[11]),
                                                                         'price_unit': float(line[12]),
                                                                         'name': product.name,
                                                                         #'tax_id': [(6,0,tax_ar)] if tax_ar else False,
                                                                         'order_id': sale.id})
                            if pricelist_id:
                                sale.pricelist_id = pricelist_id.id
                            if company:
                                sale.company_id = company.id
                            if tax_ar:
                                order_line.tax_id = [(6,0,tax_ar)]
                            request.session['import_sale_order'].add(sale.id)
                            request.session['confirm_sale_order'].append(sale.id)
                            
        
        sale_ids = request.session['import_sale_order']
        array = []
        confirm_sale_order_auto = self.env['ir.config_parameter'].sudo().search([('key','=', 'confirm_sale')])
        if confirm_sale_order_auto:
            if request.session['import_sale_order']:
                for i in request.session['import_sale_order']:
                    array.append(int(i))
                    request.session['awb_sale_order'] = True
                    sale_confirm = self.env['sale.order'].sudo().search([('id','=', int(i))])
                    if sale_confirm.state in ['draft','sent']:
                        sale_confirm.action_confirm()
                    request.session['awb_sale_order'] = False
        return sale_ids
        
    def auto_confirm_sale_order(self):
        """Confirm the sale order manually for imported records"""
        order_c = request.session['confirm_sale_order']
        sales = self.env['sale.order'].search([('id','in',order_c),('import_id_awb','!=',False),('state','in',['draft','sent'])])
        for sale in sales:
            request.session['awb_sale_order'] = True
            sale.action_confirm()
            request.session['awb_sale_order'] = False                                            
                    