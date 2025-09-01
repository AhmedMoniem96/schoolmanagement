from odoo import models , fields

class FeeStructureLines(models.Model):
    _name = "fee.structure.lines"
    _description = "Fee Structure Lines"


    name = fields.Char(string='Name')
    fee_type_id = fields.Many2one(
        "fee.type",
        string="Fee Type",
        required=True)

    amount = fields.Float(string='Amount',related='fee_type_id.amount')


    school_fee_id = fields.Many2one('school.fee.structure')

