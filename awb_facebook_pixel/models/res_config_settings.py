# -*- coding: utf-8 -*-
"""imports from odoo lib"""
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):  # @UndefinedVariable
    """Variable declaration"""
    _inherit = 'res.config.settings'

    facebook_pixel_key = fields.Char(related='website_id.facebook_pixel_key', readonly=False,)  # @UndefinedVariable

    @api.depends('website_id')
    def website_facebook_pixel(self):
        """to update the true or falase condition"""
        self.website_facebook_pixel = bool(self.facebook_pixel_key)

    def inverse_website_facebook_pixel(self):
        """if not key, it will set to false"""
        if not self.website_facebook_pixel:
            self.facebook_pixel_key = False

    website_facebook_pixel = fields.Boolean(string='Facebook Pixel', compute=website_facebook_pixel, inverse=inverse_website_facebook_pixel,)  # @UndefinedVariable
    
    @api.model
    def set_values(self):
        """Set value to ir.config_parameter"""
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('fb_pixel_key', self.facebook_pixel_key)
        return res
 
    @api.model
    def get_values(self):
        """get value from ir.config_parameter"""
        res = super(ResConfigSettings, self).get_values()
        IrConfigParameter = self.env['ir.config_parameter'].sudo()
        fb_pixel_key_db = IrConfigParameter.get_param('fb_pixel_key')
        res.update(
            facebook_pixel_key = int(fb_pixel_key_db)
        )
        return res
    
    def pixel_key(self):
        res_config_pixel_key = self.env['ir.config_parameter'].sudo().search([('key','=', 'fb_pixel_key')])
        result = int(res_config_pixel_key.value)
        return result