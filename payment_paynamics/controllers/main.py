# -*- coding: utf-8 -*-


import logging
import pprint
import werkzeug
from odoo import http
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.http import request
import base64

import xml.etree.ElementTree as ET

_logger = logging.getLogger(__name__)


class PaynamicsController(http.Controller):
    _notify_url = '/shop/payment/paynamics/ipn/'
    _return_url = '/shop/payment/paynamics/dpn/'
    _cancel_url = '/shop/payment/paynamics/cancel/'

    def _parse_pdt_response(self, response):
        """ Parse a XML response for verification.
        """
        result = {}
        resp = response['paymentresponse'].replace(' ','+')
        resp_bytes = base64.b64decode(resp)
        responseXml = ET.fromstring(resp_bytes)
        request_id = responseXml.find('application').find('request_id')
        result['request_id'] = request_id.text 
        payment_date = responseXml.find('application').find('timestamp')
        result['payment_date'] = payment_date.text 
        response_id = responseXml.find('application').find('response_id')
        result['response_id'] = response_id.text 
        response_code = responseXml.find('responseStatus').find('response_code')
        result['response_code'] = response_code.text
        _logger.info('***_parse_pdt_response*** %s', result)
        return result

    def paynamics_validate_data(self, **post):
        """ Paynamics IPN: three steps validation to ensure data correctness

         - step 1: return an empty HTTP 200 response -> will be done at the end
           by returning ''
         - step 2: POST the complete, unaltered message back to Paynamics
         (preceded
           by cmd=_notify-validate or _notify-synch for PDT), with
           same encoding
         - step 3: paynamics send either VERIFIED or INVALID (single word) for
         IPN or SUCCESS or FAIL (+ data) for PDT

        Once data is validated, process it. """
        res = False
        reference = post.get('request_id')
        _logger.info('****** %s', reference)  # debug
        tx = None
        if reference:
            _logger.info('***sds*** %s', reference)  # debug
            tx = request.env['payment.transaction'].sudo().search([
                ('reference', '=', reference)])
        _logger.info('Beginning Paynamics DPN form_feedback with post data** %s',
                     tx.acquirer_id.id)  # debug

        if post.get('response_code') in ['GR001','GR002']:
            _logger.info('Paynamics: validated data')
            res = request.env[
                'payment.transaction'].sudo().form_feedback(post, 'paynamics')
            if not res and tx:
                tx.sudo().update({'state': 'error','state_message': 'Validation error occured. Please contact your \
                    administrator.'})
        elif post.get('response_code') in ['GR036']:
            _logger.warning(
                'Paynamics: Signature Verification failed')
            if tx:
                tx.sudo().update({'state': 'error','state_message': 'Signature Verification failed. Please contact your \
                    administrator.'})
        elif post.get('response_code') in ['GR028','GR053']:
            _logger.warning('Paynamics: CANCELLED')
            if tx:
                tx.sudo().update({'state':'cancel','state_message':'Paynamics: Transaction cancelled by user'})
                #tx.sudo()._set_transaction_cancel()
        else:
            _logger.warning('Paynamics: unrecognized paynamics answer, received %s \
            instead of VERIFIED/SUCCESS or INVALID/FAIL' % post.get(
                'response_code'))
            if tx:
                tx.sudo().update({'state': 'error','state_message': 'Unrecognized error from \
                Paynamics. Please contact your administrator.'})
        return res

    @http.route('/shop/payment/paynamics/ipn/', type='http', auth='none',
                methods=['POST'], csrf=False)
    def paynamics_ipn(self, **post):
        """ Paynamics IPN. """
        _logger.info('Beginning Paynamics IPN form_feedback with post \
                data %s', pprint.pformat(post))  # debug
        
        response = self._parse_pdt_response(post)       
        try:
            self.paynamics_validate_data(**response)
        except ValidationError:
            _logger.exception('Unable to validate the Paynamics payment')
        return ''

    @http.route('/shop/payment/paynamics/dpn', type='http', auth="none",
                methods=['POST', 'GET'], csrf=False)
    def paynamics_dpn(self, **post):
        """ Paynamics DPN """
        _logger.info('Beginning Paynamics DPN form_feedback with post \
            data %s', pprint.pformat(post))  # debug
        return werkzeug.utils.redirect('/shop/payment/validate')

    @http.route('/shop/payment/paynamics/cancel', type='http', auth="none",
                csrf=False)
    def paynamics_cancel(self, **post):
        """ When the user cancels its Paynamics payment: GET on this route """
        _logger.info('Beginning Paynamics cancel with post \
            data %s', pprint.pformat(post))  # debug
        return werkzeug.utils.redirect('/shop/confirmation')
