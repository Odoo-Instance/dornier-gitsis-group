'''
Created on 29 November 2018

@author: Denbho
'''
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    purchase_tax_category = fields.Selection([
                                ('G', 'VAT on Purchase (Goods)'),
                                ('CG', 'Capital Goods'),
                                ('GNQ', 'Goods not Qualified for Input Tax'),
                                ('I', 'Importation of Goods'),
                                ('S', 'VAT on Purchase (Services)'),
                                ('SNQ', 'Services not Qualified for Input Tax'),
                                ('SNR', 'Services by Non-Residents')
                                ], string="Purchase Tax Category")
    withholding_tax_account_id = fields.Many2one('account.tax', string="CWT Account", domain="[('type_tax_use', 'in', ['withholding']), ('withholding_type', 'in', ['EWT'])]")

    @api.onchange('withholding_tax_account_id')
    def _onchange_cwt(self):
        if self.withholding_tax_account_id:
            ids = [i.id for i in self.taxes_id]
            ids.append(self.withholding_tax_account_id.id)
            self.taxes_id = [(6, 0, set(ids))]

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(PurchaseOrderLine, self).onchange_product_id()
        self.purchase_tax_category = self.product_id.purchase_tax_category
        self.withholding_tax_account_id = self.order_id.partner_id and self.order_id.partner_id.ewt and self.order_id.partner_id.ewt.id
        ids = [i.id for i in self.taxes_id]
        if self.withholding_tax_account_id:
            ids.append(self.withholding_tax_account_id.id)
        self.taxes_id = [(6, 0, set(ids))]
        return res
