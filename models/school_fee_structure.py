from odoo import api , fields , models , _
from odoo.exceptions import ValidationError

class SchoolFreeStructure(models.Model):
    _name = "school.fee.structure"

    name = fields.Char(string='Name')
    academic_year_id = fields.Many2one('academic.year',string='Academic Year')
    semester_id = fields.Many2one('school.semester',string='Semester')
    fee_line_ids = fields.One2many('fee.structure.lines','school_fee_id')

    empty_book_lines = fields.Boolean(string='Empty')
    activation_date = fields.Date(string="Activation Date")
    # books_ids = fields.Many2many(
    #     'product.product', 'fee_struct_books_rel', 'fee_id', 'product_id',
    #     string="Books", domain="[('school_item_type','=','book')]"
    # )
    # supplies_ids = fields.Many2many(
    #     'product.product', 'fee_struct_supplies_rel', 'fee_id', 'product_id',
    #     string="Supplies", domain="[('school_item_type','=','supplies')]"
    # )
    # uniform_ids = fields.Many2many(
    #     'product.product', 'fee_struct_uniform_rel', 'fee_id', 'product_id',
    #     string="Uniform", domain="[('school_item_type','=','uniform')]"
    # )

    subtotal_amount = fields.Monetary(
        string='Subtotal',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True,
    )
    discount_amount = fields.Monetary(
        string='Discount',
        currency_field='currency_id',
        default=0.0
    )
    total_amount = fields.Monetary(
        string='Total Amount',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True,
    )

    currency_id = fields.Many2one('res.currency',string='Currency',default=lambda self: self.env.company.currency_id.id,
                                  required=True)

    _sql_constraints = [
        (
            'check_discount_range',
            'CHECK (discount_amount >= 0 AND discount_amount <= subtotal_amount)',
            'Discount must be non-negative and cannot exceed the subtotal.'
        ),
    ]


    # items_total = fields.Monetary(
    #     string="Items Total",
    #     currency_field='currency_id',
    #     compute='_compute_totals',
    #     store=True,
    # )

    @api.onchange('empty_book_lines')
    def _onchange_empty_book_lines(self):
        if self.empty_book_lines:
            self.fee_line_ids = [(5, 0, 0)]


    @api.depends('fee_line_ids.subtotal', 'discount_amount')
    def _compute_totals(self):
        for rec in self:
            subtotal = sum(rec.fee_line_ids.mapped('subtotal'))
            rec.subtotal_amount = subtotal
            rec.total_amount = max(subtotal - (rec.discount_amount or 0.0), 0.0)

    @api.constrains('discount_amount')
    def _check_discount_not_exceed_subtotal(self):
        for rec in self:
            if rec.discount_amount and rec.discount_amount < 0:
                raise ValidationError(_("Discount cannot be negative."))
            if (rec.discount_amount or 0.0) > (rec.subtotal_amount or 0.0):
                raise ValidationError(_("Discount cannot exceed the subtotal."))

