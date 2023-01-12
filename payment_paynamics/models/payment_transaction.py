# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint

from werkzeug import urls

from odoo import _, models, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.payment_paynamics.controllers.main import PaynamicsController
from odoo.http import request
import json
import base64
import hashlib
import requests

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    
    paynamics_method = fields.Char(string="Paynamics Method")

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return paynamics-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific rendering values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider != 'paynamics':
            return res

        payload = self._paynamics_prepare_payment_request_payload()
        _logger.info("sending '/payments' request for link creation:\n%s", pprint.pformat(payload))
        # payment_data = self.acquirer_id._paynamics_make_request('/payments', data=payload)

        # The acquirer reference is set now to allow fetching the payment status after redirection
        # self.acquirer_reference = payment_data.get('id')

        # Extract the checkout URL from the payment data and add it with its query parameters to the
        # rendering values. Passing the query parameters separately is necessary to prevent them
        # from being stripped off when redirecting the user to the checkout URL, which can happen
        # when only one payment method is enabled on paynamics and query parameters are provided.
        checkout_url = payload['redirectUrl']
        parsed_url = urls.url_parse(checkout_url)
        url_params = urls.url_decode(parsed_url.query)
        return {'api_url': checkout_url, 'url_params': url_params}

    def _paynamics_prepare_payment_request_payload(self):
        """ Create the payload for the payment request based on the transaction values.

        :return: The request payload
        :rtype: dict
        """
        user_lang = self.env.context.get('lang')
        base_url = self.acquirer_id.get_base_url()
        redirect_url = urls.url_join(base_url, PaynamicsController._return_url)
        notify_url = urls.url_join(base_url, PaynamicsController._notify_url)
        cancel_url = urls.url_join(base_url, PaynamicsController._cancel_url)

        username = self.acquirer_id.paynamics_user
        password = self.acquirer_id.paynamics_password
        
        url = self.acquirer_id.paynamics_checkout_url+"/v1/rpf/transactions/rpf"
        Authorization = base64.b64encode(str(username+password).encode('utf-8'))
        
        merchantid = self.acquirer_id.paynamics_seller_account
        mkey = self.acquirer_id.paynamics_pdt_token
        
        
        
        paynamics_method = ""
        
        if self.paynamics_method == "paynamics_cash":
            paynamics_method = "gc"
        elif self.paynamics_method == "paynamics_creditcard":
            paynamics_method = "gpap_cc_ph"
        elif self.paynamics_method == "paynamics_allchannel":
            paynamics_method = ""
        
        request_id = self.reference
        notification_url = notify_url
        response_url = redirect_url
        cancel_url = cancel_url
        pmethod = ""
        pchannel = paynamics_method
        amount = f"{self.amount:.2f}"
        currency = self.currency_id.name or "PHP"
        payment_notification_status = "1"
        payment_notification_channel = "1"
        
        
        rawTrx = (merchantid + request_id + notification_url + response_url + cancel_url + pmethod + amount + currency + payment_notification_status + payment_notification_channel + mkey).encode('utf-8');
        
        signatureTrx = hashlib.sha512(rawTrx).hexdigest()
        
        fname = self.partner_id.name
        lname = ""
        mname = ""
        email = self.partner_email or self.partner_id.email or ""
        phone = self.partner_phone or self.partner_id.phone or ""
        mobile = self.partner_id.mobile or ""
        dob = ""
        
        raw = (fname + lname + mname + email + phone + mobile + dob + mkey).encode('utf-8');
        signature =  hashlib.sha512(raw).hexdigest()
        
        
        order_details = {}
        orders = []
        
        
        partner_invoice_id = self.sale_order_ids.mapped("partner_invoice_id")[0]
        partner_shipping_id = self.sale_order_ids.mapped("partner_shipping_id")[0]
        
        for sale_id in self.sale_order_ids:
            for line_id in sale_id.order_line:
                line_val = {
                            "itemname": line_id.product_id.name,
                            "quantity": str(int(line_id.product_uom_qty)),
                            "unitprice": str("{:.2f}".format(line_id.price_unit)),
                            "totalprice": str("{:.2f}".format(line_id.price_total))
                          }
                orders.append(line_val)
                
        order_details = {
                "orders":orders,
                "subtotalprice": str("{:.2f}".format(sum(self.sale_order_ids.mapped("amount_total")))),
                "shippingprice": "0.00",
                "discountamount": "0.00",
                "totalorderamount": str("{:.2f}".format(sum(self.sale_order_ids.mapped("amount_total"))))
            }
        
        payload = json.dumps({
          "transaction": {
            "request_id": request_id,
            "notification_url": notification_url,
            "response_url": response_url,
            "pmethod":"",
            "cancel_url": cancel_url,
            "pchannel": pchannel,
            "payment_notification_status": payment_notification_status,
            "payment_notification_channel": payment_notification_channel,
            "amount": amount,
            "currency": currency,
            "trx_type": "sale",
            "signature": signatureTrx
          },
          "billing_info": {
            "billing_address1": partner_invoice_id and partner_invoice_id.street,
            "billing_address2": partner_invoice_id and partner_invoice_id.street2,
            "billing_city": partner_invoice_id and partner_invoice_id.city,
            "billing_state": partner_invoice_id.state_id and partner_invoice_id.state_id.name or "",
            "billing_country": partner_invoice_id.country_id and partner_invoice_id.country_id.code or "",
            "billing_zip": partner_invoice_id.zip
          },
          "shipping_info": {
            "shipping_address1": partner_shipping_id and partner_shipping_id.street,
            "shipping_address2": partner_shipping_id and partner_shipping_id.street2,
            "shipping_city": partner_shipping_id and partner_shipping_id.city,
            "shipping_state": partner_shipping_id.state_id and partner_shipping_id.state_id.name or "",
            "shipping_country": partner_shipping_id.country_id and partner_shipping_id.country_id.code or "",
            "shipping_zip": partner_shipping_id.zip
          },
          "customer_info": {
            "fname": fname,
            "lname": lname,
            "mname": mname,
            "email": email,
            "phone": phone,
            "mobile": mobile,
            "dob": dob,
            "signature": signature
          },
          "order_details": order_details
        })
        headers = {
          'Content-Type': 'application/json'
        }
        
        _logger.info('Payload %s', payload)
    
        response = requests.request("POST", url, auth=(username, password), headers=headers, data=payload)
        # print(response.text)
        response = response.json()
        
        _logger.info('response %s', response)
        
        if response.get("response_code", "") != "GR033":
            raise ValidationError(
                "Paynamics: " + _(
                    "Received notification data not acknowledged by Paynamics:\n%s",
                    pprint.pformat(response)
                )
            )
        
        return {
            'description': self.reference,
            'amount': {
                'currency': self.currency_id.name,
                'value': f"{self.amount:.2f}",
            },

            # Since paynamics does not provide the transaction reference when returning from
            # redirection, we include it in the redirect URL to be able to match the transaction.
            'redirectUrl': response.get('redirect_url'),
        }
        

    @api.model
    def _get_tx_from_feedback_data(self, provider, post):
        tx = super()._get_tx_from_feedback_data(provider, post)
        if provider != 'paynamics':
            return tx

        reference = post.get('request_id')
        if not reference:
            raise ValidationError(
                "paynamics: " + _(
                    "Received data with missing reference %(r)s.",
                    r=reference
                )
            )

        tx = self.sudo().search([('reference', '=', reference), ('provider', '=', 'paynamics')])
        if not tx:
            raise ValidationError(
                "paynamics: " + _("No transaction found matching reference %s.", reference)
            )

        return tx


    def _process_feedback_data(self, post):
        super()._process_feedback_data(post)
        if self.provider != 'paynamics':
            return
        
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
            self._set_done()
        elif post.get('response_code') in ['GR036']:
            _logger.warning(
                'Paynamics: Signature Verification failed')
            self.update({'state': 'error','state_message': 'Signature Verification failed. Please contact your \
                    administrator.'})
        elif post.get('response_code') in ['GR028','GR053']:
            _logger.warning('Paynamics: CANCELLED')
            if tx:
                self.sudo().update({'state':'cancel','state_message':'Paynamics: Transaction cancelled by user'})
        elif post.get('response_code') in ['GR033']:
            _logger.warning('Paynamics: pending')
            if tx:
                self.sudo().update({'state':'pending','state_message':'Paynamics: Transaction is pending.'})
                #tx.sudo()._set_transaction_cancel()
        else:
            _logger.warning('Paynamics: unrecognized paynamics answer, received %s \
            instead of VERIFIED/SUCCESS or INVALID/FAIL' % post.get(
                'response_code'))
            self.sudo().update({'state': 'error','state_message': 'Unrecognized error from \
                Paynamics. Please contact your administrator. \n '+str(post.get("response_message", ""))+' \n'+str(post.get("response_advise", ""))})
        

