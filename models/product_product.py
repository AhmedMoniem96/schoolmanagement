from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductProduct(models.Model):
    _inherit = 'product.product'

    book_level = fields.Selection(
        [('level_1', 'Grade 1'), ('level_2', 'Grade 2')],
        string='Book Level',
        default='level_1',
    )

    school_item_type = fields.Selection(
        [('supplies', 'Supplies'), ('book', 'Book'), ('uniform', 'Uniform')],
        string='School Item Type',
        default='supplies',
        index=True,
    )

    book_code = fields.Char(string='Book Code', copy=False, readonly=True, index=True)

    _sql_constraints = [
        ('book_code_unique', 'unique(book_code)', 'Book Code must be unique.'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.school_item_type == 'book' and not rec.book_code:
                rec.book_code = rec._next_book_code()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'school_item_type' in vals:
            for rec in self:
                if rec.school_item_type == 'book' and not rec.book_code:
                    rec.book_code = rec._next_book_code()
        return res

    def _next_book_code(self):
        code = self.env['ir.sequence'].next_by_code('school.book.seq')
        return code or '/'
