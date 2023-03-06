# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class Company(models.Model):
    _inherit = "res.company"
    
    automation_sale_file = fields.Binary(string="Upload File")
    automation_sale_file_type = fields.Selection([('CSV', 'CSV File'),('XLS', 'XLS File')],string='File Type', default='XLS')