'''
Created on 28 November 2018

@author: Denbho
'''
from odoo import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_tax_category = fields.Selection([('Goods', 'Goods'), ('Services', 'Services')], string="Sale Tax Category")
    sale_tax_type = fields.Selection([
                            ('Vat on Sales', 'VAT on Sales'),
                            ('Sales to Government', 'Sales to Government'),
                            ('Zero Rated Sales', 'Zero Rated Sale'),
                            ('Tax Exempt Sales', 'Tax Exempt Sales'),
                        ], string="Tax Type", default="Vat on Sales")
    taxes_id = fields.Many2many('account.tax', 'product_taxes_rel', 'prod_id', 'tax_id', string='Customer Taxes',
        domain=[('sale_tax_type', 'in', ['Vat on Sales', 'Sales to Government', 'Zero Rated Sales'])])
    supplier_taxes_id = fields.Many2many('account.tax', 'product_supplier_taxes_rel', 'prod_id', 'tax_id', string='Vendor Taxes',
        domain=[('type_tax_use', '=', 'purchase')])
    purchase_tax_category = fields.Selection([
                                ('G', 'VAT on Purchase (Goods)'),
                                ('CG', 'Capital Goods'),
                                ('GNQ', 'Goods not Qualified for Input Tax'),
                                ('I', 'Importation of Goods'),
                                ('S', 'VAT on Purchase (Services)'),
                                ('SNQ', 'Services not Qualified for Input Tax'),
                                ('SNR', 'Services by Non-Residents')
                                ], string="Purchase Tax Category")

    @api.onchange("purchase_tax_category")
    def _onchange_purchase_tax(self):
        vals = {}
        tax_domain = [("type_tax_use", "in", [self.purchase_tax_category]), ('company_id', '=', self.company_id.id)]
        if self.sale_tax_category == 'G': tax_domain.append(('goods', '=', True))
        elif self.sale_tax_category == 'S': tax_domain.append(('services', '=', True))
        elif self.sale_tax_category == 'CG': tax_domain.append(('cg', '=', True))
        elif self.sale_tax_category == 'GNQ': tax_domain.append(('gnq', '=', True))
        elif self.sale_tax_category == 'I': tax_domain.append(('importation', '=', True))
        elif self.sale_tax_category == 'SNQ': tax_domain.append(('snq', '=', True))
        elif self.sale_tax_category == 'SNR': tax_domain.append(('snr', '=', True))
        vals['domain'] = {
            "supplier_taxes_id": tax_domain,
        }
        return vals

    @api.onchange("sale_tax_category", "sale_tax_type")
    def _onchange_sale_tax(self):
        vals = {}
        tax_domain = [("type_tax_use", "in", [self.sale_tax_type]), ('company_id', '=', self.company_id.id)]
        if self.sale_tax_category == 'Goods': tax_domain.append(('goods', '=', True))
        else: tax_domain.append(('services', '=', True))
        vals['domain'] = {
            "taxes_id": tax_domain,
        }
        return vals

class AccountTax(models.Model):
    _inherit = 'account.tax'

    sale_tax_type = fields.Selection([
                            ('Vat on Sales', 'Vat on Sales'),
                            ('Sales to Government', 'Sales to Government'),
                            ('Zero Rated Sales', 'Zero Rated Sale'),
                            ('Tax Exempt Sales', 'Tax Exempt Sales'),
                        ], string="Tax Type", default="Vat on Sales")
    withholding_type = fields.Selection([
                        ('CWT', 'CWT'),
                        ('EWT', 'EWT')
                    ], string="Withholding Type")
    type_tax_use = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchases'),
        ('withholding', 'Withholding'),
        ('none', 'None')], string='Tax Scope', required=True, default="sale",
        help="Determines where the tax is selectable. Note : 'None and Sales (Due to PH Standard)' means a tax can't be used by itself, however it can still be used in a group.")
    withholding_tax = fields.Boolean(string="Withholding Tax")
    withholding_classification = fields.Selection([('person', 'Individual'), ('company', 'Corporation')], string="Withholding Type")
    description = fields.Text(string="Description")
    goods = fields.Boolean(string="Goods")
    services = fields.Boolean(string="Services")
    snq = fields.Boolean(string="Services Not Qualified for Input Tax")
    gnq = fields.Boolean(string="Goods Not Qualified for Input Tax")
    snr = fields.Boolean(string="Services by Non-residents")
    importation = fields.Boolean(string="Importation of Goods")
    cg = fields.Boolean(string="Capital Goods")


    @api.onchange('type_tax_use')
    def _onchange_type_tax_use(self):
        if self.type_tax_use and self.type_tax_use == 'withholding': self.withholding_tax = True
        else: self.withholding_tax = False

    @api.multi
    def name_get(self):
        res = super(AccountTax, self).name_get()
        data = []
        for i in self:
            display_value = ''
            display_value += i.name or ""
            display_value += ' ['
            display_value += i.description or ""
            display_value += ']'
            data.append((i.id, display_value))
        return data


class ResPartner(models.Model):
    _inherit = 'res.partner'

    line_of_business_id = fields.Many2one('line.of.business', string="Line of Business")

    rdo = fields.Char(string="RDO", size=3, default="000")
    vat = fields.Char(string="TIN", size=9)
    partner_code = fields.Char(string="Partner Code")
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    middle_name = fields.Char(string="Middle Name")
    cwt = fields.Many2one('account.tax', string="Default CWT", domain="[('type_tax_use', '=', 'withholding')]")
    ewt = fields.Many2one('account.tax', string="Default EWT", domain="[('type_tax_use', '=', 'withholding')]")


    @api.onchange('first_name', 'last_name', 'middle_name', 'company_type')
    def _onchange_classification(self):
        if self.first_name and self.last_name and not self.company_type in ['company']:
            if not self.middle_name: self.name = "%s, %s"%(self.last_name, self.first_name)
            else: self.name = "%s, %s  %s"%(self.last_name, self.first_name, self.middle_name)



class ResCompany(models.Model):
    _inherit = 'res.company'

    vat = fields.Char(string="TIN", size=9)
    rdo = fields.Char(string="RDO", size=3)
    line_of_business_id = fields.Many2one('line.of.business', string="Line of Business", requied=True)
    established_date = fields.Date(string="Established Date")
    classification = fields.Selection([('person', 'Individual'), ('company', 'Non-Individual')], string="Classication", requied=True, default="company")
    tax_type = fields.Selection([('Percentage Tax', 'Percentage Tax'), ('Value Added Tax', 'Value Added Tax'), ('Tax Exempt', 'Tax Exempt ')],
                                string="Tax Exemption Type")
    tax_rate_type = fields.Selection([
                        ('1702EX', '1702EX - Exempt organization under tax'),
                        ('1702MX', '1702MX - Mixed income subject to Income Tax'),
                        ('1702RT', '1702RT - Regular Tax Rate')
                    ], string="Tax Rate Type", default="1702RT")
    type_of_enterprise = fields.Selection(selection=[('single', 'Single Proprietorship'), ('corporation_partnership', 'Corporation/Partnership')])
    business_name = fields.Char(string="Business Name", help="Business Name Registration is issued for single proprietorship in the Philippines")
    certificate_of_registration = fields.Char(string="Certificate of Registration", help="Certificate of Registration is issued for partnership or corporation")
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    middle_name = fields.Char(string="Middle Name")

    @api.onchange('first_name', 'last_name', 'middle_name', 'classification')
    def _onchange_classification(self):
        if self.first_name and self.last_name and self.classification == 'Individual':
            if not self.middle_name: self.name = "%s, %s"%(self.last_name, self.first_name)
            else: self.name = "%s, %s  %s"%(self.last_name, self.first_name, self.middle_name)

class LineofBusiness(models.Model):
    _name='line.of.business'

    name = fields.Char(string="Line Of Business")
    description = fields.Text(string="Description")
