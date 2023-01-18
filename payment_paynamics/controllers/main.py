# -*- coding: utf-8 -*-


import logging
import pprint
import werkzeug
from odoo import http
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.http import request
import base64
import json
import xml.etree.ElementTree as ET
import requests

_logger = logging.getLogger(__name__)


class PaynamicsController(http.Controller):
    _notify_url = '/shop/payment/paynamics/ipn/'
    _return_url = '/shop/payment/paynamics/dpn/'
    _cancel_url = '/shop/payment/paynamics/cancel/'

    @http.route('/shop/payment/paynamics/ipn/', type='json', auth='public',
                methods=['POST','GET'], csrf=False)
    def paynamics_ipn_return_from_redirect(self, **post):
        _logger.info("received Paynamics return post args:\n%s", pprint.pformat(post))
        data = json.loads(request.httprequest.data)
        """ Paynamics return """
        _logger.info("received Paynamics return data:\n%s", pprint.pformat(data))
        try:
            request.env['payment.transaction'].sudo().with_context(uid=1, user=2)._handle_feedback_data('paynamics', data)
            print(request.env.uid)
        except Exception as e:
            _logger.info("received Paynamics warning:\n%s", pprint.pformat(str(e)))
            request.env['payment.transaction'].sudo()._handle_feedback_data('paynamics', post)
            
        return 'Success'

    @http.route('/shop/payment/paynamics/dpn', type='http', auth="public",
                methods=['POST', 'GET'], csrf=False)
    def paynamics_dpn(self, **post):
        data = {}
        _logger.info("received Paynamics return post args:\n%s", pprint.pformat(post))
        if request.httprequest.data:
            data = json.loads(request.httprequest.data)
        """ paynamics Notify """
        _logger.info("received paynamics notification data:\n%s", pprint.pformat(data))
        if data or post:
            try:
                request.env['payment.transaction'].sudo()._handle_feedback_data('paynamics', data)
            except:
                request.env['payment.transaction'].sudo()._handle_feedback_data('paynamics', post)
            
        return request.redirect('/payment/status')
    

    @http.route('/shop/payment/paynamics/cancel', type='http', auth="public",
                csrf=False)
    def paynamics_cancel(self, **post):
        if request.httprequest.data:
            data = json.loads(request.httprequest.data)
        # data = json.loads(request)
        """ When the user cancels its Paynamics payment: GET on this route """
        _logger.info('Beginning Paynamics cancel with post \
            data %s', pprint.pformat(post))  # debug
        # request.env['payment.transaction'].sudo()._handle_feedback_data('paynamics', data)
        transaction_id = request.session.get('__website_sale_last_tx_id', False)
        if transaction_id:
            request.env['payment.transaction'].sudo().browse(transaction_id)._set_canceled()
        return werkzeug.utils.redirect('/shop/confirmation')


