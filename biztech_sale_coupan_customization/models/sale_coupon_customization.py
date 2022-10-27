# -*- coding:utf-8 -*-
# Part of AppJetty. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.tools.misc import formatLang

class SaleCouponReward(models.Model):
    _inherit = 'sale.coupon.reward'

    discount_apply_on = fields.Selection(selection_add=[('specific_category', 'On Specific Product Category')])
    discount_specific_product_category_id = fields.Many2one('product.category', string="Product Category",
        help="Product Category that will be discounted if the discount is applied on a specific product")

    @api.multi
    def name_get(self):
        """
        Returns a complete description of the reward
        """
        result = []
        for reward in self:
            reward_string = ""
            if reward.reward_type == 'product':
                reward_string = _("Free Product - %s" % (reward.reward_product_id.name))
            elif reward.reward_type == 'discount':
                if reward.discount_type == 'percentage':
                    reward_percentage = str(reward.discount_percentage)
                    if reward.discount_apply_on == 'on_order':
                        reward_string = _("%s%% discount on total amount" % (reward_percentage))
                    elif reward.discount_apply_on == 'specific_product':
                        reward_string = _("%s%% discount on %s" % (reward_percentage, reward.discount_specific_product_id.name))
                    elif reward.discount_apply_on == 'specific_category':
                        reward_string = _("%s%% discount on %s" % (reward_percentage, reward.discount_specific_product_category_id.name))
                    elif reward.discount_apply_on == 'cheapest_product':
                        reward_string = _("%s%% discount on cheapest product" % (reward_percentage))
                elif reward.discount_type == 'fixed_amount':
                    program = self.env['sale.coupon.program'].search([('reward_id', '=', reward.id)])
                    reward_string = _("%s %s discount on total amount" % (str(reward.discount_fixed_amount), program.currency_id.name))
            result.append((reward.id, reward_string))
        return result


class SaleCouponProgram(models.Model):
    _inherit = 'sale.coupon.program'

    def write(self, vals):
        res = super(SaleCouponProgram, self).write(vals)
        reward_fields = [
            'reward_type', 'reward_product_id', 'discount_type', 'discount_percentage',
            'discount_apply_on', 'discount_specific_product_id', 'discount_fixed_amount',
            'discount_specific_product_category_id'
        ]
        if any(field in reward_fields for field in vals):
            self.mapped('discount_line_product_id').write({'name': self[0].reward_id.name_get()[0][1]})
        return res



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Adding new Discount Type for Product Category
    def _get_reward_values_discount(self, program):
        if program.discount_type == 'fixed_amount':
            return [{
                'name': _("Discount: ") + program.name,
                'product_id': program.discount_line_product_id.id,
                'price_unit': - self._get_reward_values_discount_fixed_amount(program),
                'product_uom_qty': 1.0,
                'product_uom': program.discount_line_product_id.uom_id.id,
                'is_reward_line': True,
                'tax_id': [(4, tax.id, False) for tax in program.discount_line_product_id.taxes_id],
            }]
        reward_dict = {}
        lines = self._get_paid_order_lines()
        if program.discount_apply_on == 'cheapest_product':
            line = self._get_cheapest_line()
            if line:
                discount_line_amount = line.price_unit * (program.discount_percentage / 100)
                if discount_line_amount:
                    taxes = line.tax_id
                    if self.fiscal_position_id:
                        taxes = self.fiscal_position_id.map_tax(taxes)

                    reward_dict[line.tax_id] = {
                        'name': _("Discount: ") + program.name,
                        'product_id': program.discount_line_product_id.id,
                        'price_unit': - discount_line_amount,
                        'product_uom_qty': 1.0,
                        'product_uom': program.discount_line_product_id.uom_id.id,
                        'is_reward_line': True,
                        'tax_id': [(4, tax.id, False) for tax in taxes],
                    }
        elif program.discount_apply_on in ['specific_product', 'on_order', 'specific_category']:
            if program.discount_apply_on == 'specific_product':
                # We should not exclude reward line that offer this product since we need to offer only the discount on the real paid product (regular product - free product)
                free_product_lines = self.env['sale.coupon.program'].search([('reward_type', '=', 'product'), ('reward_product_id', '=', program.discount_specific_product_id.id)]).mapped('discount_line_product_id')
                lines = lines.filtered(lambda x: x.product_id == program.discount_specific_product_id or x.product_id in free_product_lines)

            # For Product Category
            if program.discount_apply_on == 'specific_category':
                product_ids = self.env['product.product'].search([('categ_id', '=', program.discount_specific_product_category_id.id)])
                lines = lines.filtered(lambda x: x.product_id.id in product_ids.ids)

            for line in lines:
                discount_line_amount = self._get_reward_values_discount_percentage_per_line(program, line)

                if discount_line_amount:

                    if line.tax_id in reward_dict:
                        reward_dict[line.tax_id]['price_unit'] -= discount_line_amount
                    else:
                        taxes = line.tax_id
                        if self.fiscal_position_id:
                            taxes = self.fiscal_position_id.map_tax(taxes)

                        tax_name = ""
                        if len(taxes) == 1:
                            tax_name = " - " + _("On product with following tax: ") + ', '.join(taxes.mapped('name'))
                        elif len(taxes) > 1:
                            tax_name = " - " + _("On product with following taxes: ") + ', '.join(taxes.mapped('name'))

                        reward_dict[line.tax_id] = {
                            'name': _("Discount: ") + program.name + tax_name,
                            'product_id': program.discount_line_product_id.id,
                            'price_unit': - discount_line_amount,
                            'product_uom_qty': 1.0,
                            'product_uom': program.discount_line_product_id.uom_id.id,
                            'is_reward_line': True,
                            'tax_id': [(4, tax.id, False) for tax in taxes],
                        }

        # If there is a max amount for discount, we might have to limit some discount lines or completely remove some lines
        max_amount = program._compute_program_amount('discount_max_amount', self.currency_id)
        if max_amount > 0:
            amount_already_given = 0
            for val in list(reward_dict):
                amount_to_discount = amount_already_given + reward_dict[val]["price_unit"]
                if abs(amount_to_discount) > max_amount:
                    reward_dict[val]["price_unit"] = - (max_amount - abs(amount_already_given))
                    add_name = formatLang(self.env, max_amount, currency_obj=self.currency_id)
                    reward_dict[val]["name"] += "( " + _("limited to ") + add_name + ")"
                amount_already_given += reward_dict[val]["price_unit"]
                if reward_dict[val]["price_unit"] == 0:
                    del reward_dict[val]
        return reward_dict.values()