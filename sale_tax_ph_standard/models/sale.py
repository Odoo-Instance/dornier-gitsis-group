'''
Created on 29 November 2018

@author: Denbho
'''
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sale_tax_category = fields.Selection([('Goods', 'Goods'), ('Services', 'Services')], string="Category")
    withholding_tax_account_id = fields.Many2one('account.tax', string="CWT Account", domain="[('type_tax_use', 'in', ['withholding']), ('withholding_type', 'in', ['CWT'])]")
    sale_tax_type = fields.Selection([
                            ('Vat on Sales', 'Vat on Sales'),
                            ('Sales to Government', 'Sales to Government'),
                            ('Zero Rated Sales', 'Zero Rated Sale'),
                            ('Tax Exempt Sales', 'Tax Exempt Sales'),
                        ], string="Tax Type", default="Vat on Sales")

    @api.onchange("sale_tax_category", "sale_tax_type", "product_id", "order_id.partner_id.cwt", "order_id.partner_id.cwt")
    def _onchange_sale_tax(self):
        vals = {}
        tax_domain = [
            ("type_tax_use", "in", ['sale', 'withholding']),
            # ('sale_tax_type', '=',self.sale_tax_type),
            ('company_id', '=', self.order_id.company_id.id)]
        if self.sale_tax_category == 'Goods': tax_domain.append(('goods', '=', True))
        else: tax_domain.append(('services', '=', True))
        vals['domain'] = {
                "tax_id": tax_domain,
            }
        return vals

    @api.onchange('withholding_tax_account_id')
    def _onchange_cwt(self):
        if self.withholding_tax_account_id:
            ids = [i.id for i in self.tax_id]
            ids.append(self.withholding_tax_account_id.id)
            self.tax_id = [(6, 0, set(ids))]

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        self.sale_tax_category = self.product_id.sale_tax_category
        self.sale_tax_type = self.product_id.sale_tax_type
        self.withholding_tax_account_id = self.order_id.partner_id and self.order_id.partner_id.cwt and self.order_id.partner_id.cwt.id
        ids = [i.id for i in self.tax_id]
        if self.withholding_tax_account_id:
            ids.append(self.withholding_tax_account_id.id)
        self.tax_id = [(6, 0, set(ids))]
        return res

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res['sale_tax_category'] = self.sale_tax_category
        res['sale_tax_type'] = self.sale_tax_type
        res['withholding_tax_account_id'] = self.withholding_tax_account_id.id
        return res
