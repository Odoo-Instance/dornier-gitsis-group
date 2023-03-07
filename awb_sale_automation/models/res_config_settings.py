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

    automation_sale_file = fields.Binary(related="company_id.automation_sale_file", string="Upload File", readonly=False)
    automation_sale_file_type = fields.Selection(related="company_id.automation_sale_file_type", string='File Type', default='XLS', readonly=False)

    def _find_partner_id(self, name, name2=False):
        # print('--------==>>> name, name2', name, name2)
        partner_id = self.env['res.partner'].search([('name','=', name)], limit=1)
        # print('--------==>>> partner_id', partner_id)
        if not partner_id:
            try:
                partner_id = self.env['res.partner'].create({
                    'name' : name,
                    'firstname' : name,
                })
            except Exception as e:
                partner_id = self.env['res.partner'].search([('name','=','Public user')], limit=1)
            self._cr.commit()
        return partner_id and partner_id.id or False
    
    def _find_partner_address_id(self, name, partner):
        partner_id = self.env['res.partner'].search([('name','=', name)], limit=1)
        if not partner_id:
            return partner
        return partner_id and partner_id.id or False
        
    def _find_sale_order_template_id(self, name):
        sale_order_template_id = self.env['sale.order.template'].search([('name','=', name)], limit=1)
        return sale_order_template_id and sale_order_template_id.id or False

    def _find_pricelist_id(self, name):
        pricelist_id = self.env['product.pricelist'].search([('name','=', name)], limit=1)
        if not pricelist_id:
            pricelist_id = self.env['product.pricelist'].search([], limit=1)   
        return pricelist_id and pricelist_id.id or False

    def _find_payment_term_id(self, name):
        payment_term_id = self.env['account.payment.term'].search([('name','=', name)], limit=1)
        return payment_term_id and payment_term_id.id or False

    def _find_carrier_id(self, name):
        carrier_id = self.env['delivery.carrier'].search([('name','=', name)], limit=1)
        return carrier_id and carrier_id.id or False
    
    def _find_user_id(self, name):
        user_id = self.env['res.users'].search([('name','=', name)], limit=1)
        return user_id and user_id.id or False
    
    def _find_product_id(self, name, name2=False):
        product_id = self.env['product.product'].search([('name','=', name)], limit=1)
        return product_id
    
    def _find_team_id(self, name):
        partner = self.env['crm.team'].search([('name','=', name)], limit=1)
        return partner and partner.id or False
    
    def _find_tag_ids(self, name):
        tag_names = name.split(',')
        tag_ids = self.env['crm.tag'].search([('name','in', tag_names)], limit=1)
        return [(6,0, tag_ids.ids)]
    
    def _find_tax_id(self, name):
        tax_names = name.split(',')
        tax_id = self.env['account.tax'].search([('name','in', tax_names)], limit=1)
        return [(6,0, tax_id.ids)]

    def _find_uom_id(self, name):
        uom_id = self.env['uom.uom'].search([('name','=', name)], limit=1)
        if not uom_id:
            uom_id = self.env['uom.uom'].search([], limit=1)
        return uom_id and uom_id.id or False
    
    def _convert_to_state_selection(self, name):
        if name == 'Quotation':
            return 'draft'
        elif name == 'Quotation Sent':
            return 'sent'
        elif name == 'Sales Order':
            return 'sale'
        elif name == 'Locked':
            return 'done'
        elif name == 'Cancelled':
            return 'cancel'
        else:
            return 'draft'

    def _convert_to_date(self, date_):
        # print('--------==>>> date_', date_)
        date_ = date_.split('.')[0]
        # print('--------==>>> date_', date_)
        if date_ and date_.isdigit():
            if isinstance(int(date_), int or float):
                awb_date = (int(date_) - 25569) * 24 * 60 * 60 * 1000
                my_datetime = datetime.fromtimestamp(awb_date / 1000)    
                return my_datetime
        elif date_ != '' and isinstance(date_, str):
            return datetime.strptime(date_, '%Y-%m-%d %H:%M:%S')
        else:
            return False

    def auto_import_sales(self):
        if self.automation_sale_file:
            if self.automation_sale_file_type == 'XLS':
                try:
                    file = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
                    file.write(binascii.a2b_base64(self.automation_sale_file))
                    file.seek(0)
                    
                    values = {}
                    workbook = xlrd.open_workbook(file.name)
                    sheet = workbook.sheet_by_index(0)
                except Exception as e:
                    raise ValidationError(_("Please Select Valid File Format !, Error : "+str(e)))
                
                last_order_id = self.env['sale.order']
                for row_no in range(sheet.nrows):
                    val = {}
                    if row_no <= 0:
                        fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
                    else:
                        line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))

                        # Customer/ID	3
                        # Customer/Name	4
                        # Invoice Address/Display Name	5
                        # Delivery Address/Name	6
                        # Quotation Template/Display Name 7	
                        # Expiration Date	8
                        # Pricelist/Pricelist Name 9	
                        # Payment Terms/Display Name 10	
                        # Delivery Method/Name 11
                        
                        # Terms and conditions 25
                        # Untaxed Amount	26
                        # Taxes	27
                        # Total	28
                        # Commitment Date	29
                        # Order Date	30
                        # Salesperson/Name	31
                        # Tags/Display Name	32
                        # Sales Channel/Display Name	33
                        # Customer Reference	34
                        # Confirmation Date	35
                        # Confirmation Mode	36
                        # Status 37
                        
                        partner_id = self._find_partner_id(line[4], line[3])

                        if line[0] != '':
                            order_vals = {
                                'name' : line[2],
                                'partner_id' : partner_id,
                                'partner_invoice_id' : self._find_partner_address_id(line[5], partner_id),
                                'partner_shipping_id' : self._find_partner_address_id(line[6], partner_id),
                                'sale_order_template_id' : self._find_sale_order_template_id(line[7]),
                                'validity_date' : self._convert_to_date(line[8]),
                                'pricelist_id' : self._find_pricelist_id(line[9]),
                                'payment_term_id' : self._find_payment_term_id(line[10]),
                                'carrier_id' : self._find_carrier_id(line[11]),
                                'note' : line[25],
                                'date_order' : self._convert_to_date(line[30]),
                                'tag_ids' : self._find_tag_ids(line[32]),
                                'user_id' : self._find_user_id(line[31]),
                                'team_id' : self._find_team_id(line[33]),
                                # Sales Channel/Display Name : 33
                                'client_order_ref' : line[34],
                                # Confirmation Date	: 35
                                # Confirmation 1Mode : 36
                                'state' : self._convert_to_state_selection(line[37]),
                            }
                            # print('--------==>>> order_vals', order_vals)
                            if order_vals.get('partner_id') == '':
                                continue

                            last_order_id = self.env['sale.order'].create(order_vals)

                        # Order Lines/Product/ID	12
                        # Order Lines/Product/Name	13
                        # Order Lines/Section/Display Name	14
                        # Order Lines/Display Name	15
                        # Order Lines/Category	16
                        # Order Lines/Tax Type	17
                        # Order Lines/CWT Account/Display Name	18
                        # rder Lines/Quantity	19
                        # Order Lines/Unit of Measure/Display Name	20
                        # Order Lines/Unit Price	21
                        # Order Lines/Taxes	22
                        # Order Lines/Discount (%)	23
                        # Order Lines/Total 24
                        product_id = self._find_product_id(line[13], line[12])
                        product_uom_id = product_id.uom_id
                        if not product_id and line[14] == '':
                            continue
                        order_line_vals = {
                            'product_id' : product_id and product_id.id or False,
                            'name' : line[14] or line[15],
                            'display_type' : 'line_section' if line[14] else False,
                            'product_uom_qty' : float(line[19]) if line[19] else 1.0,
                            'product_uom' : product_uom_id and product_uom_id.id or False,
                            'price_unit' : float(line[21]) if line[21] else 0.0,
                            'tax_id' : self._find_tax_id(line[22]),
                            'discount' : float(line[23]) if line[23] else 0.0,
                            'order_id' : last_order_id and last_order_id.id,
                        }
                        # print('--------==>>> order_line_vals', order_line_vals)
                        last_line_id = self.env['sale.order.line'].create(order_line_vals)
                        _logger.info('----------------------- row_no : %s ' % row_no)
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

                # except Exception as e:
                #     # print(e)
                #     raise ValidationError(_("Please Select Valid File Format !  or "+str(e)))


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
                    
                        
    

        
        
        
        
        
        