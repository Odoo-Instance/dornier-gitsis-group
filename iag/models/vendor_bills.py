from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class APV(models.Model):
    _inherit='account.invoice'

    requested_by = fields.Char(string="Prepared By", default="Jane Frances Tubello")
    approved_by = fields.Char(string="Approved By", default="Portia Cardel")
    checked_by = fields.Char(string="Checked By", default="Jayson Tadeo")