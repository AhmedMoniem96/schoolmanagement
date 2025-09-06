from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class SchoolFeeStructure(models.Model):
    _name = "school.fee.structure"
    _description = "School Fee Structure"

    name = fields.Char(string='Name')
    academic_year_id = fields.Many2one('academic.year', string='Academic Year')
    semester_id = fields.Many2one('school.semester', string='Semester')
    fee_line_ids = fields.One2many('fee.structure.lines', 'school_fee_id', string="Fee Lines")

    empty_book_lines = fields.Boolean(string='Empty')
    activation_date = fields.Date(string="Activation Date")

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id.id,
        required=True
    )

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

    @api.onchange(
        'discount_amount',
        'fee_line_ids',
        'fee_line_ids.quantity',
        'fee_line_ids.price_unit',
    )
    def _onchange_discount_live_guard(self):
        for rec in self:
            subtotal = sum((l.quantity or 0.0) * (l.price_unit or 0.0) for l in rec.fee_line_ids)

            if rec.discount_amount is None:
                continue

            if rec.discount_amount < 0:
                rec.discount_amount = 0.0
                return {
                    'warning': {
                        'title': _('Invalid discount'),
                        'message': _('Discount cannot be negative. It was reset to 0.'),
                    }
                }

            if rec.discount_amount > subtotal:
                rec.discount_amount = 0
                return {
                    'warning': {
                        'title': _('Discount too large'),
                        'message': _(
                            'Discount cannot exceed the subtotal (%.2f). '
                        ) % subtotal,
                    }
                }
