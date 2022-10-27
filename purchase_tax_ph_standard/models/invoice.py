'''
Created on 29 November 2018

@author: Denbho
'''
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def _prepare_invoice_line_from_po_line(self, line):
        res = super(AccountInvoice, self)._prepare_invoice_line_from_po_line(line)
        res['purchase_tax_category'] = line.purchase_tax_category
        res['withholding_tax_account_id'] = line.withholding_tax_account_id and line.withholding_tax_account_id.id
        return res

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    purchase_tax_category = fields.Selection([
                                ('G', 'VAT on Purchase (Goods)'),
                                ('CG', 'Capital Goods'),
                                ('GNQ', 'Goods not Qualified for Input Tax'),
                                ('I', 'Importation of Goods'),
                                ('S', 'VAT on Purchase (Services)'),
                                ('SNQ', 'Services not Qualified for Input Tax'),
                                ('SNR', 'Services by Non-Residents'),
                                ], string="Purchase Tax Category")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.invoice_id.type in ['in_invoice', 'in_refund']:
            self.purchase_tax_category = self.product_id.purchase_tax_category
            self.withholding_tax_account_id = self.invoice_id.partner_id and self.invoice_id.partner_id.ewt and self.invoice_id.partner_id.ewt.id or False
            ids = [i.id for i in self.invoice_line_tax_ids]
            if self.withholding_tax_account_id:
                ids.append(self.withholding_tax_account_id.id)
            self.invoice_line_tax_ids = [(6, 0, set(ids))]
            return res
