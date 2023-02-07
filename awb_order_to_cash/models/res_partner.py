# -*- coding: utf-8 -*-
"""imports from odoo"""
from odoo import fields, models,api,_  # @UnusedImport


"""inherited res.partner model for adding fields"""
class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'
    _description = "added custom fields"
    
    
    awb_fax_no = fields.Char(string="Fax no", required=False, copy = False, index=False)
    awb_customer_category = fields.Selection([('d2c', 'Direct to Consumer'),('b2b', 'Business to Business')], string="Customer Category", required=False, copy = False, index=False)
    awb_tin = fields.Char(string="Tin", required=False, copy = False, index=False)
    amount_credit_limit = fields.Monetary(string='Internal Credit Limit', default=-1)
    credit_limit_compute = fields.Monetary(
        string='Credit Limit ', default=-1,
        compute='_compute_credit_limit_compute', inverse='_inverse_credit_limit_compute',
        help='A limit of zero means no limit. A limit of -1 will use the default (company) limit.'
    )
    show_credit_limit = fields.Boolean(compute='_compute_show_credit_limit')
    awb_hold_customer = fields.Boolean(string="Hold Customer")
    
    @api.depends('amount_credit_limit')
    @api.depends_context('company')
    def _compute_credit_limit_compute(self):
        """this method is used to compute credit limit"""
        for partner in self:
            partner.credit_limit_compute = self.env.company.account_default_credit_limit if partner.amount_credit_limit == -1 else partner.amount_credit_limit

    @api.depends('credit_limit_compute')
    @api.depends_context('company')
    def _inverse_credit_limit_compute(self):
        """this method is used to inverse credit limit compute."""
        for partner in self:
            is_default = partner.credit_limit_compute == self.env.company.account_default_credit_limit
            partner.amount_credit_limit = -1 if is_default else partner.credit_limit_compute

    @api.depends_context('company')
    def _compute_show_credit_limit(self):
        """this method is used to show credit limit"""
        for partner in self:
            partner.show_credit_limit = self.env.company.account_credit_limit

    def _commercial_fields(self):
        """this method is used to add commercial fields"""
        return super(ResPartnerInherit, self)._commercial_fields() + ['amount_credit_limit']
    
"""inherited res.partner model for adding fields"""  
class Company(models.Model):
    _inherit = "res.company"
    _description = "added custom fields"
    
    awb_automation_sale_file = fields.Binary(string="Upload File")
    awb_automation_sale_file_type = fields.Selection([('csv', 'CSV'),('xls', 'XLS')],string='File Type', default='xls')
    account_credit_limit = fields.Boolean()
    account_default_credit_limit = fields.Monetary()
    credit_limit_type = fields.Selection([('warning', 'Warning'), ('block', 'Block')])