# -*- coding: utf-8 -*-
"""imports from odoo lib"""
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):  # @UndefinedVariable
    """Variable declaration"""
    _inherit = 'res.config.settings'

    facebook_page_id = fields.Char(related='website_id.facebook_page_id', readonly=False,copy=False,tracking=False,index=False,required=False,translate=True)  # @UndefinedVariable

    @api.depends('website_id')
    def website_facebook_page_id(self):
        """to update the true or false condition"""
        self.website_facebook_page_id = bool(self.facebook_page_id)

    def inverse_website_facebook_page_id(self):
        """if not key, it will set to false"""
        if not self.website_facebook_page_id:
            self.facebook_page_id = False

    website_facebook_page_id = fields.Boolean(string='Facebook Messenger', compute=website_facebook_page_id, inverse=inverse_website_facebook_page_id,copy=False,tracking=False,index=False,required=False,translate=True)  # @UndefinedVariable
    
    @api.model
    def set_values(self):
        """Set value to ir.config_parameter"""
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('fb_page_id', self.facebook_page_id)
        return res
 
    @api.model
    def get_values(self):
        """get value from ir.config_parameter"""
        res = super(ResConfigSettings, self).get_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        fb_page_id_db = IrConfigParameter.get_param('fb_page_id')
        res.update(
            facebook_page_id = int(fb_page_id_db)
        )
        return res
    
    
    def page_id(self):
        """to get the values of page_id"""
        res_config_page_id = self.env['ir.config_parameter'].sudo().search([('key','=', 'fb_page_id')])
        result = int(res_config_page_id.value)
        return result