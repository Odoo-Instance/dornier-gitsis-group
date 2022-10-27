odoo.define('payment_paynamics.processing', function (require) {
'use strict';

var ajax = require('web.ajax');
var rpc = require('web.rpc')
 var core = require('web.core');
var publicWidget = require('web.public.widget');

 var _t = core._t;

var PaymentProcessing = publicWidget.registry.PaymentProcessing;

return PaymentProcessing.include({

		displayLoading: function () {
            var msg = _t("Don't close the tab. We are processing your payment, please wait ...");
            $.blockUI({
                'message': '<h2 class="text-white"><img src="/web/static/src/img/spin.png" class="fa-pulse"/>' +
                    '    <br />' + msg +
                    '</h2>'
            });
        },
});
});