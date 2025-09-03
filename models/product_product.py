
from odoo import models , fields , api

class ProductProduct(models.Model):
    _inherit = ['product.product']


    book_level = fields.Selection([
        ('level_1', 'Grade 1'),
        ('level_2', 'Grade 2')],
        string='Book Level',default='level_1',
                                )

    school_item_type = fields.Selection([
        ('supplies','Supplies'),
        ('book','Book'),
        ('uniform','Uniform')
    ],string='school_item_types', default='supplies',index=True)

    book_code = fields.Char(string='Book Code', copy=False, readonly=True, index=True)


    # def _book_level_options(self):
    #     return [(f'level_{i}', f'Level {i}') for i in range(1, 13)]
    #
    # book_level = fields.Selection(
    #     selection=_book_level_options,
    #     string="Book Level",
    #     default='level_1',
    #     help="Educational level  target."
    # )


    @api.model_create_multi
    def _create_multi(self,vals_list):
        recs = super().create(vals_list)
        for rec in recs:
            if rec.school_item_type == 'book' and not rec.book_code:
                rec.book_code = self.env['ir.sequence'].next_by_code('school.book.seq') or '/'
        return recs

