odoo.define('awb_messenger_chat.fb_chat', function (require) {
'use strict';
	
	
	var rpc = require('web.rpc')
	/*call the function at certain interval of time*/
	setInterval(helpdeskFb,10000)
	
	function helpdeskFb() {
		var currentUrl = window.location.href;
		if (currentUrl.includes('helpdesk.team')) {
			if ($('#fb-customer-chat').length > 0) {
				rpc.query({
					model: 'res.config.settings',
					method: 'page_id',
					args: [0],
				}).then( function(result) {


					var chatBox = document.getElementById('fb-customer-chat');


					chatBox.setAttribute("page_id", result);
					chatBox.setAttribute("attribution", "biz_inbox");

					window.fbAsyncInit = function() {
						FB.init({
							xfbml: true,
							version: 'v15.0'
						});
					};

					(function(d, s, id) {
						var js, fjs = d.getElementsByTagName(s)[0];
						if (d.getElementById(id)) return;
						js = d.createElement(s); js.id = id;
						js.src = 'https://connect.facebook.net/en_US/sdk/xfbml.customerchat.js';
						fjs.parentNode.insertBefore(js, fjs);
					}(document, 'script', 'facebook-jssdk'));



				});
			}
		}
	}
	/*set time function to add the facebook page id in crm module*/
	    setInterval(checkLoaded, 10000);
	    
		
		function checkLoaded() {
			/*checked currentURL condition for respected module, not for all module.
			eg: changes should only reflect in crm not in other module.*/
			var currentUrl = window.location.href;
			if (currentUrl.includes('crm.lead')) {
  			if ($('#fb-customer-chat').length > 0) {
					rpc.query({
			model: 'res.config.settings',
			method: 'page_id',
			args: [0],
		}).then( function (result) {
			
				
		      var chatBox = document.getElementById('fb-customer-chat');
		      
		      
		      chatBox.setAttribute("page_id",result);
		      chatBox.setAttribute("attribution", "biz_inbox");
		    
		      window.fbAsyncInit = function() {
		        FB.init({
		          xfbml            : true,
		          version          : 'v15.0'
		        });
		      };
		
		      (function(d, s, id) {
		        var js, fjs = d.getElementsByTagName(s)[0];
		        if (d.getElementById(id)) return;
		        js = d.createElement(s); js.id = id;
		        js.src = 'https://connect.facebook.net/en_US/sdk/xfbml.customerchat.js';
		        fjs.parentNode.insertBefore(js, fjs);
		      }(document, 'script', 'facebook-jssdk'));
		   
					
					
		});
		}
		}
		
	}
	
	
		
		
		
});