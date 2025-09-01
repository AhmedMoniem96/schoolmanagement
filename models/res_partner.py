from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    teacher_ids = fields.One2many('school.teacher', 'partner_id', string="Teacher Records")