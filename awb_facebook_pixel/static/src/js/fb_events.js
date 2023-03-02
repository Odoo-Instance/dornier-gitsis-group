odoo.define('awb_facebook_pixel.fb_events', function (require) {
'use strict';
	
	var ajax = require('web.ajax');
	var rpc = require('web.rpc')
	
	
		
	
	
	if ($("#product_details").length > 0){
		
		rpc.query({
			model: 'res.config.settings',
			method: 'pixel_key',
			args: [0],
		}).then(function(result){
			const $product = $('#product_detail');
	        const fbproductTrackingInfo = $product.data('product-tracking-info');
			
			!function(f,b,e,v,n,t,s)
			{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
			n.callMethod.apply(n,arguments):n.queue.push(arguments)};
			if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
			n.queue=[];t=b.createElement(e);t.async=!0;
			t.src=v;s=b.getElementsByTagName(e)[0];
			s.parentNode.insertBefore(t,s)}(window, document,'script',
			'https://connect.facebook.net/en_US/fbevents.js');
			fbq('init', result);
			fbq('track', 'ViewContent', {
				  content_name: fbproductTrackingInfo.item_name,
				  content_category: fbproductTrackingInfo.item_category,
				  content_ids: fbproductTrackingInfo.item_id,
				  content_type: 'product',
				  value: fbproductTrackingInfo.price,
				  currency: fbproductTrackingInfo.currency
				 });
			
		})
//		const $product = $('#product_detail');
//        const fbproductTrackingInfo = $product.data('product-tracking-info');
//		
//		!function(f,b,e,v,n,t,s)
//		{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
//		n.callMethod.apply(n,arguments):n.queue.push(arguments)};
//		if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
//		n.queue=[];t=b.createElement(e);t.async=!0;
//		t.src=v;s=b.getElementsByTagName(e)[0];
//		s.parentNode.insertBefore(t,s)}(window, document,'script',
//		'https://connect.facebook.net/en_US/fbevents.js');
//		fbq('init', '776456150097051');
//		fbq('track', 'ViewContent', {
//			  content_name: fbproductTrackingInfo.item_name,
//			  content_category: fbproductTrackingInfo.item_category,
//			  content_ids: fbproductTrackingInfo.item_id,
//			  content_type: 'product',
//			  value: fbproductTrackingInfo.price,
//			  currency: fbproductTrackingInfo.currency
//			 });
	} else {
		console.log("Nothing to see")
	}
	
	$('#add_to_cart').click(function () {
		rpc.query({
			model: 'res.config.settings',
			method: 'pixel_key',
			args: [0],
		}).then(function(result){
			const $product = $('#product_detail');
	        const fbproductTrackingInfo = $product.data('product-tracking-info');
			
			!function(f,b,e,v,n,t,s)
			{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
			n.callMethod.apply(n,arguments):n.queue.push(arguments)};
			if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
			n.queue=[];t=b.createElement(e);t.async=!0;
			t.src=v;s=b.getElementsByTagName(e)[0];
			s.parentNode.insertBefore(t,s)}(window, document,'script',
			'https://connect.facebook.net/en_US/fbevents.js');
			fbq('init', result);
			fbq('track', 'AddToCart', {
				  content_name: fbproductTrackingInfo.item_name,
				  content_category: fbproductTrackingInfo.item_category,
				  content_ids: fbproductTrackingInfo.item_id,
				  content_type: 'product',
				  value: fbproductTrackingInfo.price,
				  currency: fbproductTrackingInfo.currency
				 });
			
		})
//		const $product = $('#product_detail');
//        const fbproductTrackingInfo = $product.data('product-tracking-info');
//		
//		!function(f,b,e,v,n,t,s)
//		{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
//		n.callMethod.apply(n,arguments):n.queue.push(arguments)};
//		if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
//		n.queue=[];t=b.createElement(e);t.async=!0;
//		t.src=v;s=b.getElementsByTagName(e)[0];
//		s.parentNode.insertBefore(t,s)}(window, document,'script',
//		'https://connect.facebook.net/en_US/fbevents.js');
//		fbq('init', '776456150097051');
//		fbq('track', 'AddToCart', {
//			  content_name: fbproductTrackingInfo.item_name,
//			  content_category: fbproductTrackingInfo.item_category,
//			  content_ids: fbproductTrackingInfo.item_id,
//			  content_type: 'product',
//			  value: fbproductTrackingInfo.price,
//			  currency: fbproductTrackingInfo.currency
//			 });
	});
	
	$('a[href="/shop/checkout?express=1"]').click(function () {
		rpc.query({
			model: 'res.config.settings',
			method: 'pixel_key',
			args: [0],
		}).then(function(result){
			var params={}
		
			ajax.jsonRpc('/facebook/cart', 'call', params ).then(function (result) { 
						!function(f,b,e,v,n,t,s)
			{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
			n.callMethod.apply(n,arguments):n.queue.push(arguments)};
			if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
			n.queue=[];t=b.createElement(e);t.async=!0;
			t.src=v;s=b.getElementsByTagName(e)[0];
			s.parentNode.insertBefore(t,s)}(window, document,'script',
			'https://connect.facebook.net/en_US/fbevents.js');
			fbq('init', result);
			
			
			fbq('track', 'InitiateCheckout', {
				contents:result
			});	
			});
			
		})
//		var params={}
//		
//		ajax.jsonRpc('/facebook/cart', 'call', params ).then(function (result) { 
//					!function(f,b,e,v,n,t,s)
//		{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
//		n.callMethod.apply(n,arguments):n.queue.push(arguments)};
//		if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
//		n.queue=[];t=b.createElement(e);t.async=!0;
//		t.src=v;s=b.getElementsByTagName(e)[0];
//		s.parentNode.insertBefore(t,s)}(window, document,'script',
//		'https://connect.facebook.net/en_US/fbevents.js');
//		fbq('init', '776456150097051');
//		
//		
//		fbq('track', 'InitiateCheckout', {
//			contents:result
//		});	
//		});
	});
	
	if($('.oe_website_sale_tx_status ').length > 0){
		rpc.query({
			model: 'res.config.settings',
			method: 'pixel_key',
			args: [0],
		}).then(function(result){
			const $trans = $('.oe_website_sale_tx_status');
			const fbTrackingInfo = $trans.data('order-tracking-info');
			!function(f,b,e,v,n,t,s)
			{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
			n.callMethod.apply(n,arguments):n.queue.push(arguments)};
			if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
			n.queue=[];t=b.createElement(e);t.async=!0;
			t.src=v;s=b.getElementsByTagName(e)[0];
			s.parentNode.insertBefore(t,s)}(window, document,'script',
			'https://connect.facebook.net/en_US/fbevents.js');
			fbq('init', result);
			fbq('track', 'Purchase', {
				  content_type: 'product',
				  value: fbTrackingInfo.value,
				  currency: fbTrackingInfo.currency,
				  contents:fbTrackingInfo.items
				 });
			
		})
//		const $trans = $('.oe_website_sale_tx_status');
//		const fbTrackingInfo = $trans.data('order-tracking-info');
//		!function(f,b,e,v,n,t,s)
//		{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
//		n.callMethod.apply(n,arguments):n.queue.push(arguments)};
//		if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
//		n.queue=[];t=b.createElement(e);t.async=!0;
//		t.src=v;s=b.getElementsByTagName(e)[0];
//		s.parentNode.insertBefore(t,s)}(window, document,'script',
//		'https://connect.facebook.net/en_US/fbevents.js');
//		fbq('init', '776456150097051');
//		fbq('track', 'Purchase', {
//			  content_type: 'product',
//			  value: fbTrackingInfo.value,
//			  currency: fbTrackingInfo.currency,
//			  contents:fbTrackingInfo.items
//			 });
	} 
	
});