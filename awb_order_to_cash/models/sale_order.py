# -*- coding: utf-8 -*-
"""imports from python lib"""
from datetime import datetime,timedelta

"""imports from odoo"""
from odoo import fields, models, api, _  # @UnusedImport
from odoo.http import request
from odoo.exceptions import ValidationError

"""inherited sale.order model for order due remainder. changed _id to _ids"""
class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    _description = "remainder alert"
    
    awb_product_ids = fields.Many2many('product.product',copy=False, index= False)
    partner_credit = fields.Monetary(related='partner_id.commercial_partner_id.credit', readonly=True)
    partner_credit_limit = fields.Monetary(related='partner_id.credit_limit_compute', readonly=True)
    show_partner_credit_warning = fields.Boolean(compute='_compute_show_partner_credit_warning')
    credit_limit_type = fields.Selection(related='company_id.credit_limit_type')
    import_id_awb = fields.Char(string="Import ID")  
    
    @api.model
    def create(self, vals):
        """create method"""
        res = super(SaleOrderInherit, self).create(vals)
        awb_order = res.order_line
        p_id = []
        for i in awb_order:
            p_id.append(i.product_id.id)
        res.awb_product_ids = [(6,0,p_id)]
        return res
    
    @api.onchange('partner_id')
    def _onchange_partner_id_awb(self):
        """while onchanging the customer in sale order , it wll check the customer is in hold state."""
        if self.partner_id.awb_hold_customer:
            raise ValidationError(_("You are not allowed to proceed futher. Please contact Administrator."))
        
    
    @api.onchange('order_line')
    def _onchange_prder_line_product(self):
        """onchange method to update the product id to awb_product_ids"""
        p_id = []
        for i in self.order_line.product_id:
            p_id.append(i.id)
        if len(p_id) > 0:
            self.awb_product_ids = [(6,0,p_id)]
        
    def sale_product_update(self):
        """"scheduler product update"""
        sale_order = self.env['sale.order'].search([])
        for sale in sale_order:
            p_id = []
            for i in sale.order_line:
                p_id.append(i.product_id.id)
            sale.awb_product_ids = [(6,0,p_id)]
    
    def email_due_remainder(self):
        """due remainder for sale.order """
        sale_order = self.env['sale.order'].search([('payment_term_id','!=',False),('state','in',['sale','draft'])])
        for sale in sale_order:
            order_date = sale.date_order
            payment_terms_date = sale.payment_term_id.line_ids.days
            today = datetime.now()
            if payment_terms_date == 15:
                pay_terms = 15
                if (today.date() - order_date.date()).days in [0,8,10,12,14]:
                    context = {}
                    days = pay_terms - ((today.date() - order_date.date()).days)
                    context.update({'email_from':self.env.user.email,
                                    'users': self.env.user,
                                    'days':days})
                    self.env.ref('awb_order_to_cash.due_remainder_email_template').with_context(**context).send_mail(sale.id, force_send=True)
            elif payment_terms_date == 30:
                if (today.date() - order_date.date()).days in [0,23,25,27,29]:
                    pay_terms = 30
                    context = {}
                    days = pay_terms - ((today.date() - order_date.date()).days)
                    context.update({'email_from':self.env.user.email,
                                    'users': self.env.user,
                                    'days':days})
                    self.env.ref('awb_order_to_cash.due_remainder_email_template').with_context(**context).send_mail(sale.id, force_send=True)
            elif payment_terms_date == 45:
                if (today.date() - order_date.date()).days in [0,38,40,42,44]:
                    pay_terms = 45
                    context = {}
                    days = pay_terms - ((today.date() - order_date.date()).days)
                    context.update({'email_from':self.env.user.email,
                                    'users': self.env.user,
                                    'days':days})
                    self.env.ref('awb_order_to_cash.due_remainder_email_template').with_context(**context).send_mail(sale.id, force_send=True)
            elif payment_terms_date == 60:
                if (today.date() - order_date.date()).days in [0,53,55,57,59]:
                    pay_terms = 60
                    context = {}
                    days = pay_terms - ((today.date() - order_date.date()).days)
                    context.update({'email_from':self.env.user.email,
                                    'users': self.env.user,
                                    'days':days})
                    self.env.ref('awb_order_to_cash.due_remainder_email_template').with_context(**context).send_mail(sale.id, force_send=True)
          
    @api.depends('partner_credit_limit', 'partner_credit', 'order_line',
                 'company_id.account_default_credit_limit', 'company_id.account_credit_limit')
    def _compute_show_partner_credit_warning(self):
        """"this is used to show warning and compute total due."""
        for order in self:
            account_credit_limit = order.company_id.account_credit_limit
            company_limit = order.partner_credit_limit == -1 and order.company_id.account_default_credit_limit
            partner_limit = order.partner_credit_limit + order.amount_total > 0 and order.partner_credit_limit
            partner_credit = order.partner_credit + order.amount_total
            order.show_partner_credit_warning = account_credit_limit and \
                                                ((company_limit and partner_credit > company_limit) or \
                                                (partner_limit and partner_credit > partner_limit))

    def _prepare_confirmation_values(self):
        
        if request.session.get('awb_sale_order'):
            return {
                'state': 'sale',
                'date_order': self.date_order
            }
        else:
            return {
                'state': 'sale',
                'date_order': fields.Datetime.now()
            }
    
    
    def action_confirm(self):
        """this def is used to block the confirmation of order, when the warning type is in block"""
        result = super(SaleOrderInherit, self).action_confirm()
        for so in self:
            if so.show_partner_credit_warning and so.credit_limit_type == 'block' and \
                    so.partner_credit + so.amount_total > so.partner_credit_limit:
                raise ValidationError(_("You cannot exceed credit limit !"))
        
        is_delivery_set_to_done = self.env['ir.config_parameter'].sudo().search([('key','=', 'is_delivery_set_to_done')])
        create_invoice = self.env['ir.config_parameter'].sudo().search([('key','=', 'create_invoice')])
        validate_invoice = self.env['ir.config_parameter'].sudo().search([('key','=', 'validate_invoice')])
        
        if request.session.get('awb_sale_order'):
            for order in self:
                if is_delivery_set_to_done and order.picking_ids: 
                    for picking in self.picking_ids:
                        picking.action_assign()
                        picking.action_set_quantities_to_reservation()
                        picking.action_confirm()
                        picking.button_validate()
    
                if create_invoice and not order.invoice_ids:
                    order._create_invoices()
                if validate_invoice and order.invoice_ids:
                    for invoice in order.invoice_ids:
                        invoice.action_post()

        return result
    
    def update_hold_customer(self):
        """update hold customer functions """
        sale_order = self.env['sale.order'].search([('payment_term_id','!=',False),('state','in',['sale','draft'])])
        
        for sale in sale_order:
            order_date = sale.date_order
            payment_terms_date = sale.payment_term_id.line_ids.days
            today = datetime.now()
            if payment_terms_date == 15:
                pay_terms = 15
                end_date = (order_date + timedelta(days=pay_terms)).strftime("%Y-%m-%d %H:%M:%S")
                end  = datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")
                if (today.date() > end.date()):
                    sale.partner_id.awb_hold_customer = True
            elif payment_terms_date == 30:
                pay_terms = 30
                end_date = (order_date + timedelta(days=pay_terms)).strftime("%Y-%m-%d %H:%M:%S")
                end  = datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")
                if (today.date() > end.date()):
                    sale.partner_id.awb_hold_customer = True
            elif payment_terms_date == 45:
                pay_terms = 45
                end_date = (order_date + timedelta(days=pay_terms)).strftime("%Y-%m-%d %H:%M:%S")
                end  = datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")
                if (today.date() > end.date()):
                    sale.partner_id.awb_hold_customer = True
            elif payment_terms_date == 60:
                pay_terms = 60
                end_date = (datetime.now() + timedelta(days=pay_terms)).strftime("%Y-%m-%d %H:%M:%S")
                end  = datetime.strptime(end_date,"%Y-%m-%d %H:%M:%S")
                if (today.date() > end.date()):
                    sale.partner_id.awb_hold_customer = True


