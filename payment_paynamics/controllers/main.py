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

_logger = logging.getLogger(__name__)


class PaynamicsController(http.Controller):
    _notify_url = '/shop/payment/paynamics/ipn/'
    _return_url = '/shop/payment/paynamics/dpn/'
    _cancel_url = '/shop/payment/paynamics/cancel/'

    @http.route('/shop/payment/paynamics/ipn/', type='json', auth='none',
                methods=['POST','GET'], csrf=False)
    def paynamics_ipn_return_from_redirect(self, **post):
        _logger.info("received Paynamics return post args:\n%s", pprint.pformat(post))
        data = json.loads(request.httprequest.data)
        """ Paynamics return """
        _logger.info("received Paynamics return data:\n%s", pprint.pformat(data))
        try:
            request.env['payment.transaction'].sudo()._handle_feedback_data('paynamics', data)
        except:
            request.env['payment.transaction'].sudo()._handle_feedback_data('paynamics', post)
            
        return 'Success'

    @http.route('/shop/payment/paynamics/dpn', type='http', auth="none",
                methods=['POST', 'GET'], csrf=False, cors="*")
    def paynamics_dpn(self, **post):
        _logger.info("received Paynamics return post args:\n%s", pprint.pformat(post))
        data = json.loads(request.httprequest.data)
        """ paynamics Notify """
        _logger.info("received paynamics notification data:\n%s", pprint.pformat(data))
        try:
            request.env['payment.transaction'].sudo()._handle_feedback_data('paynamics', data)
        except:
            request.env['payment.transaction'].sudo()._handle_feedback_data('paynamics', post)
            
        return request.redirect('/payment/status')
    

    @http.route('/shop/payment/paynamics/cancel', type='http', auth="none",
                csrf=False)
    def paynamics_cancel(self, **post):
        # data = json.loads(request)
        """ When the user cancels its Paynamics payment: GET on this route """
        _logger.info('Beginning Paynamics cancel with post \
            data %s', pprint.pformat(post))  # debug
        # request.env['payment.transaction'].sudo()._handle_feedback_data('paynamics', data)
        return werkzeug.utils.redirect('/shop/confirmation')


