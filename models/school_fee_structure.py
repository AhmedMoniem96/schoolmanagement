from odoo import api , fields , models

class SchoolFreeStructure(models.Model):
    _name = "school.fee.structure"

    name = fields.Char(string='Name')
    academic_year_id = fields.Many2one('academic.year',string='Academic Year')
    semester_id = fields.Many2one('school.semester',string='Semester')
    fee_line_ids = fields.One2many('fee.structure.lines','school_fee_id')
    book_ids = fields.Many2many('product.product')

    # total_amount = fields.Float(string='Total Amount',compute="_compute_total_amount",inverse='_inverse_total_amount')
    empty_book_lines = fields.Boolean(string='Empty')
    activation_date = fields.Date(string="Activation Date")
    total_amount = fields.Monetary(
        string='Total Amount',
        currency_field='currency_id',
        compute='_compute_total_amount',
        store=True,
    )
    currency_id = fields.Many2one('res.currency',string='Currency',default=lambda self: self.env.company.currency_id.id,
                                  required=True)



    @api.onchange('empty_book_lines')
    def _onchange_empty_book_lines(self):
        if self.empty_book_lines:
            self.book_ids = [(5,0,0)]


    def _inverse_total_amount(self):
        for rec in self:
            amount_per_line = rec.total_amount / len(rec.fee_line_ids)
            for line in rec.fee_line_ids:
                line.amount = amount_per_line

    @api.depends('fee_line_ids.amount')
    def _compute_total_amount(self):
        for record in self:
            amount_in_a_list = sum(record.fee_line_ids.mapped('amount'))
            record.total_amount = amount_in_a_list


