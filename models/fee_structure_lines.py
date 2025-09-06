from odoo import models , fields , api , _
from odoo.exceptions import ValidationError



class FeeStructureLines(models.Model):
    _name = "fee.structure.lines"
    _description = "Fee Structure Lines"


    name = fields.Char(string='Description')
    fee_type_id = fields.Many2one(
        "fee.type",
        string="Fee Type",
        required=True)

    amount = fields.Float(string='Amount',related='fee_type_id.amount',store=True)

    product_id = fields.Many2one('product.product', string="Product")
    semester_id = fields.Many2one(related='school_fee_id.semester_id', store=True)
    academic_year_id = fields.Many2one(related='school_fee_id.academic_year_id', store=True)
    create_date = fields.Datetime(string="Created On", readonly=True)

    school_fee_id = fields.Many2one('school.fee.structure',string='Fee Structure',required=True,ondelete='cascade')
    currency_id = fields.Many2one(related='school_fee_id.currency_id',store=True,readonly=True)
    price_unit = fields.Monetary(string='Unit Price',currency_field='currency_id')
    quantity = fields.Float(string='Quantity',default=1.0)
    subtotal = fields.Monetary(string='Sub Total',currency_field='currency_id',compute='_compute_subtotal',store=True)

    @api.depends('quantity','price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = (line.quantity or 0.0)*(line.price_unit or 0.0)

    @api.onchange('fee_type_id')
    def _onchange_fee_type_id(self):
        for line in self:
            if line.fee_type_id:
                line.price_unit = line.fee_type_id.amount or 0.0

    @api.constrains('quantity','price_unit')
    def _check_non_negative(self):
        for line in self:
            if line.quantity < 0:
                raise ValidationError(_("quantity can't be negative"))
            if line.price_unit < 0:
                raise ValidationError(_("Price_Unit can't be negative"))





