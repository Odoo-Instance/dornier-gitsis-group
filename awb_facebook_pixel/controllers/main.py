"""imports from odoo"""
from odoo import fields, http, _  # @UnusedImport
from odoo.http import request

"""imports from odoo addons"""
from odoo.addons.website.controllers.main import Website  # @UnresolvedImport @UnusedImport
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager  # @UnresolvedImport @UnusedImport
from odoo.osv.expression import AND, OR  # @UnusedImport

class CustomerPortal(CustomerPortal):   
    
    @http.route(['/facebook/cart'], type='json', auth="public", website=True, sitemap=False)
    def facebook_pixelcart(self, access_token=None, revive='', **post):
        """
        Main cart management + abandoned cart revival
        access_token: Abandoned cart SO access token
        revive: Revival method when abandoned cart. Can be 'merge' or 'squash'
        """
        
        cart_items=[]
        order = request.website.sale_get_order()
        if order and order.state != 'draft':
            request.session['sale_order_id'] = None
            order = request.website.sale_get_order()
        if order.website_order_line:
            for i in order.website_order_line:
                items = {'content_name': i.name_short,
                       'content_category': i.product_id.categ_id.display_name,
                       'content_ids': i.product_id.id,
                       'content_type': 'product',
                       'value': i.price_reduce_taxexcl,
                       'currency': i.currency_id.display_name,
                        'num_items':i.product_uom_qty
                        }
                
                cart_items.append(items)
        
        
        
        return cart_items