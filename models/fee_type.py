from odoo import models, fields

class FeeType(models.Model):
    _name = "fee.type"
    _description = "Fee Type"

    name = fields.Char(string="Name", required=True)
    amount = fields.Float(string="Amount", required=True)

    _sql_constraints = [
        ('fee_type_name_uniq', 'unique(name)', 'Fee Type name must be unique.')
    ]
