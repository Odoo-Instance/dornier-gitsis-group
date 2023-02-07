# -*- coding: utf-8 -*-
"""imports from python lib"""
from datetime import datetime

"""imports from odoo"""
from odoo import fields, models, api, _  # @UnusedImport

"""inherited sale.order model for add the new field"""
class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'
    _description = "sale order payment method"
    
    awb_payment_methods = fields.Many2many('payment.acquirer',string='Payment Methods',copy=False, index= False)
    
"""Display Payment Method as per customer selected"""   
class AccountPaymentRegisterInherit(models.TransientModel):
    _inherit = 'account.payment.register'
    
    @api.model
    def _getJournal(self):
        journal = []   
        invoice_ids = self.env['account.move'].search([('id','=',self.env.context.get('active_id'))])
        for invoice in invoice_ids:
            partner_name = invoice.partner_id.name
            partner_ids = self.env['res.partner'].search([('name','=',partner_name)])
            for partner in partner_ids:
                if partner.awb_payment_methods:
                    for payment_method in partner.awb_payment_methods:
                        journal_ids = self.env['account.journal'].search([('name','=',payment_method.name)])
                        journal.append(journal_ids.name)
                else:
                    journal_ids = self.env['account.journal'].search([])
                    for journal_name in journal_ids:
                        journal.append(journal_name.name)
        return [('name','in',journal)]

    """Set the default Payment Methods""" 
    @api.model
    def default_pay_methods(self):
        journal = []   
        invoice_ids = self.env['account.move'].search([('id','=',self.env.context.get('active_id'))])
        for invoice in invoice_ids:
            partner_name = invoice.partner_id.name
            partner_ids = self.env['res.partner'].search([('name','=',partner_name)])
            for partner in partner_ids:
                if partner.awb_payment_methods:
                    for payment_method in partner.awb_payment_methods:
                        journal_ids = self.env['account.journal'].search([('name','=',payment_method.name)],limit=1)
                else:
                    journal_ids = self.env['account.journal'].search([],limit=1)
        return journal_ids
    

    journal_id = fields.Many2one('account.journal', store=True, readonly=False, domain=_getJournal, default=default_pay_methods)  
    
    