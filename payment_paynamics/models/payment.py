# coding: utf-8

import logging
import dateutil.parser
import pytz
from hashlib import md5
from urllib.parse import urlencode, quote_plus
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_paynamics.controllers.main import PaynamicsController
import hashlib
import base64
from odoo.http import request
import socket


_logger = logging.getLogger(__name__)


class AcquirerPaynamics(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('paynamics', 'Paynamics')])
    paynamics_seller_account = fields.Char(
        'Merchant ID', groups='base.group_user',
        help='The Merchant ID is used to ensure communications coming from \
            Paynamics are valid and secured.')
    paynamics_pdt_token = fields.Char(string='Merchant Key', help='Payment Data \
        Transfer allows you to receive notification of successful payments as \
        they are made.', groups='base.group_user')
    

    def _get_feature_support(self):
        """Get advanced feature support by provider.

        Each provider should add its technical in the corresponding
        key for the following features:
            * fees: support payment fees computations
            * authorize: support authorizing payment (separates
                         authorization and capture)
            * tokenize: support saving payment data in a payment.tokenize
                        object
        """
        res = super(AcquirerPaynamics, self)._get_feature_support()
        res['fees'].append('paynamics')
        return res

    @api.model
    def _get_paynamics_urls(self, environment):
        """Paynamics URLS """
        if environment == 'prod':
            return 'https://ptiapps.paynamics.net/webpayment/Default.aspx'
        else:
            return 'https://testpti.payserv.net/webpayment/Default.aspx'

    @api.multi
    def paynamics_compute_fees(self, amount, currency_id, country_id):
        """ Compute Paynamics fees.

            :param float amount: the amount to pay
            :param integer country_id: an ID of a res.country, or None. This is
                                       the customer's country, to be compared
                                       to the acquirer company country.
            :return float fees: computed fees
        """
        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.country_id.id == country.id:
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = (percentage / 100.0 * amount) + fixed / (1 - percentage / 100.0)
        return fees

    def _build_sign(self, val):
        """ Building MD5 hash signature using posted values """
        data_string = urlencode(val, quote_via=quote_plus)
        return md5(data_string.encode('utf-8')).hexdigest()

    @api.multi
    def paynamics_form_generate_values(self, values):
        """ Generate Paynamics form values to be sent """
       
        base_url = self.env[
            'ir.config_parameter'].sudo().get_param('web.base.url')
        
        hostname = socket.gethostname()   
        IPAddr = socket.gethostbyname(hostname)
        
        partner = self.env['res.partner'].sudo().browse(values['partner_id'])
        
        mid = self.paynamics_seller_account
        requestid = values['reference']
        ipaddress = IPAddr
        noturl = urls.url_join(base_url,PaynamicsController._notify_url)
        resurl = urls.url_join(base_url,PaynamicsController._return_url)
        cancelurl = urls.url_join(base_url,PaynamicsController._cancel_url)
        fname = values.get('partner_first_name')
        lname = values.get('partner_last_name')
        addr1 = partner.street if partner.street else ''
        addr2 = partner.street2 if partner.street2 else ''
        city = values.get('partner_city') if values.get('partner_city') else ''
        state = values.get('partner_state').name if values.get('partner_state').name else ''
        country = values.get('partner_country').name if values.get('partner_country').name else ''
        zip = values.get('partner_zip') if values.get('partner_zip') else ''
        sec3d = "try3d"
        email = values.get('partner_email') if values.get('partner_email') else ''
        phone = values.get('partner_phone') if values.get('partner_phone') else ''
        mobile =  partner.mobile if partner.mobile else ''
        clientip = request.httprequest.remote_addr
        amount = str("{:.2f}".format(values['amount']))
        
        currency = self.company_id.currency_id.symbol        
        cert = self.paynamics_pdt_token
        _logger.info('***paynamics_form_validate*** %s', mid + requestid + ipaddress + noturl + resurl + fname + lname + "" + addr1 + addr2 + city + state + country + zip + email + phone + clientip + amount + currency.upper() + sec3d + cert)
        message = (mid + requestid + ipaddress + noturl + resurl + fname + lname + "" + addr1 + addr2 + city + state + country + zip + email + phone + clientip + amount + currency.upper() + sec3d + cert).encode()#cert.encode()
        
        payment_transaction = self.env['payment.transaction'].search([
            ('reference', '=', values['reference'])])
        
        linexml = ""
        
        sale_order_ids =  payment_transaction.sale_order_id
        
        if sale_order_ids:
            line_ids = self.env['sale.order.line'].sudo().search([
                ('order_id', '=', sale_order_ids.id)])
            
            for lines in line_ids:   
                print(lines.product_id.name)   
                linexml += "<Items>"
                linexml += "<itemname>"+lines.product_id.name+"</itemname>"
                linexml += "<quantity>"+str(int(lines.product_uom_qty)) +"</quantity>"
                linexml += "<amount>"+str("{:.2f}".format(lines.price_unit))+"</amount>"
                linexml += "</Items>"
       
        strxml = ""
        strxml += "<?xml version='1.0' encoding='utf-8' ?>"        
        strxml += "<Request>"
        strxml += "<mid>"+mid+ "</mid>"
        strxml += "<request_id>" + requestid + "</request_id>"
        strxml += "<ip_address>" + ipaddress + "</ip_address>";
        strxml += "<notification_url>" + noturl + "</notification_url>"
        strxml += "<response_url>" + resurl + "</response_url>"
        strxml += "<cancel_url>" + cancelurl + "</cancel_url>"
        strxml += "<mtac_url>"+resurl+"</mtac_url>"
        strxml += "<descriptor_note></descriptor_note>"
        strxml += "<fname>" + fname + "</fname>"
        strxml += "<lname>" + lname + "</lname>"
        strxml += "<mname></mname>"
        strxml += "<address1>" + addr1 + "</address1>"
        strxml += "<address2>" + addr2 + "</address2>"
        strxml += "<city>"+ city +"</city>"
        strxml += "<state>" + state + "</state>"
        strxml += "<country>" +country + "</country>"
        strxml += "<zip>" +zip + "</zip>"
        strxml += "<email>" + email + "</email>"
        strxml += "<phone>" + phone + "</phone>"
        strxml += "<mobile>" + mobile + "</mobile>"
        strxml += "<client_ip>" + clientip + "</client_ip>"
        strxml += "<amount>"+amount+"</amount>"
        strxml += "<currency>" + currency.upper()+ "</currency>"
        strxml += "<trxtype>sale</trxtype>"
        strxml += "<orders>"
        strxml += "<items>"
        strxml += linexml
        strxml += "</items>"
        strxml += "</orders>"
    
        strxml += "<secure3d>" +sec3d + "</secure3d>"
        strxml += "<signature>" +hashlib.sha512(message).hexdigest() + "</signature>"
        strxml += "</Request>"
        _logger.info('***paynamics_form_validate*** %s', strxml)
        b64string =  base64.b64encode(strxml.encode('utf-8'))
        return {"payment_values":b64string}

    @api.multi
    def paynamics_get_form_action_url(self):
        self.ensure_one()
        #environment = 'prod' if self.state == 'enabled' else 'test'
        return self._get_paynamics_urls(self.environment)


class TxPaynamics(models.Model):
    _inherit = 'payment.transaction'

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    @api.model
    def _paynamics_form_get_tx_from_data(self, data):
        reference = data.get('request_id')
        if not reference:
            error_msg = _('Paynamics: received data with missing \
                reference (%s) or txn_id (%s)') % (reference)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        # find tx -> @TDENOTE use txn_id ?
        txs = self.env['payment.transaction'].search([
            ('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'Paynamics: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    @api.multi
    def _paynamics_form_get_invalid_parameters(self, data):
        """
        Checking the response paymentID and amount sent
        """
        invalid_parameters = []
        _logger.info('Received a notification from Paynamics with IPN \
            version %s', data.get('notify_version'))
        if data.get('test_ipn'):
            _logger.warning(
                'Received a notification from Paynamics using sandbox'
            ),

        # TODO: txn_id: shoudl be false at draft, set afterwards,
        # and verified with txn details
        if self.acquirer_reference and data.get(
                'response_id') != self.acquirer_reference:
            invalid_parameters.append(('response_id', data.get(
                'response_id'), self.acquirer_reference))

        return invalid_parameters
    
    @api.multi
    def _paynamics_form_validate(self, data):
        """
        Update reference payment ID from Paynamics
        """
        _logger.info('***paynamics_form_validate*** %s', data)
        status = data.get('response_code')
        res = {
            'acquirer_reference': data.get('response_id'),
        }
        if status in ['GR001','GR002']:
            _logger.info('Validated Paynamics payment for tx %s: set as \
                done' % (self.reference))
            try:
                # dateutil and pytz don't recognize abbreviations PDT/PST
                tzinfos = {
                    'PST': -8 * 3600,
                    'PDT': -7 * 3600,
                }
                date = dateutil.parser.parse(data.get(
                    'payment_date'), tzinfos=tzinfos).astimezone(
                        pytz.utc).replace(tzinfo=None)
            except:
                date = fields.Datetime.now()
            res.update(state='done', date=date)
            return self.write(res)

        else:
            error = 'Received unrecognized status for Paynamics \
                payment %s: %s, set as error' % (self.reference, status)
            _logger.info(error)
            res.update(state='cancel',state_message=error)
            return self.write(res)
