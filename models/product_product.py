
from odoo import models , fields , api

class ProductProduct(models.Model):
    _inherit = ['product.product']


    book_level = fields.Selection([
        ('level_1', 'Grade 1'),
        ('level_2', 'Grade 2')],
        string='Book Level',default='level_1',
                                )

    # def _book_level_options(self):
    #     return [(f'level_{i}', f'Level {i}') for i in range(1, 13)]
    #
    # book_level = fields.Selection(
    #     selection=_book_level_options,
    #     string="Book Level",
    #     default='level_1',
    #     help="Educational level  target."
    # )
