'''
Created on 29 November 2018

@author: Denbho
'''
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"


    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice', 'invoice_id.date', 'withholding_tax_account_id')
    def _compute_price(self):
        super(AccountInvoiceLine, self)._compute_price()
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
            self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
            self.price_total = taxes['total_included'] if taxes else self.price_subtotal
            withholding = 0.0
            if taxes['taxes']:
                for i in taxes['taxes']:
                    if i['name'] == self.withholding_tax_account_id.name:
                        withholding = i['amount']

                self.withholding = withholding
                self.vat_amount = self.price_total - self.price_subtotal - withholding

    vat_amount = fields.Monetary(string='VAT Amount',
        store=True, readonly=True, compute='_compute_price')
    withholding = fields.Monetary(string='CWT',
        store=True, readonly=True, compute='_compute_price', help="Withholding Tax Amount")
    withholding_tax_account_id = fields.Many2one('account.tax', string="CWT Account", domain="[('type_tax_use', 'in', ['withholding'])]")
    sale_tax_category = fields.Selection([('Goods', 'Goods'), ('Services', 'Services')], string="Category")
    sale_tax_type = fields.Selection([
                            ('Vat on Sales', 'Vat on Sales'),
                            ('Sales to Government', 'Sales to Government'),
                            ('Zero Rated Sales', 'Zero Rated Sale'),
                            ('Tax Exempt Sales', 'Tax Exempt Sales'),
                        ], string="Tax Type", default="Vat on Sales")

    @api.onchange('withholding_tax_account_id')
    def _onchange_cwt(self):
        if self.withholding_tax_account_id:
            ids = [i.id for i in self.invoice_line_tax_ids]
            ids.append(self.withholding_tax_account_id.id)
            self.invoice_line_tax_ids = [(6, 0, set(ids))]


    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.invoice_id.type in ['out_invoice', 'out_refund']:
            self.sale_tax_category = self.product_id.sale_tax_category
            self.sale_tax_type = self.product_id.sale_tax_type
            self.withholding_tax_account_id = self.invoice_id.partner_id and self.invoice_id.partner_id.cwt and self.invoice_id.partner_id.cwt.id
            ids = [i.id for i in self.invoice_line_tax_ids]
            if self.withholding_tax_account_id:
                ids.append(self.withholding_tax_account_id.id)
            self.invoice_line_tax_ids = [(6, 0, set(ids))]
            return res
