from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class StockPickingInherit(models.Model):
    _inherit='stock.picking'

    prepared_by = fields.Char(string="Prepared By")
    received_by = fields.Char(string="Received By")

    picking_type_id_code_related = fields.Selection(related="picking_type_id.code")

class PurchaseOrderInherited(models.Model):
    _inherit = 'purchase.order'

    prepared_by = fields.Char(string="Prepared By", default="Christopher Bebing")
    approved_by = fields.Char(string="Approved By", default="Ms. Lulu Punongbayan")
