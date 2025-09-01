from odoo import models, fields, api
from odoo.tools import format_date

class School(models.Model):
    _name = "school.school"
    _description = "School"
    _inherit = ['mail.thread','mail.activity.mixin','school.followers']

    name = fields.Char("Name")
    address_id = fields.Many2one("res.partner", string="Address")
    establishment_date = fields.Date("Establishment Date")
    branch_ids = fields.One2many("school.branch", "school_id", string="Branches")
    establishment_date_str = fields.Char("Establishment Date (String)", compute="_compute_establishment_date_str")
    class_ids = fields.One2many('school.class', 'school_id', string='Classes')



    @api.depends("establishment_date")
    def _compute_establishment_date_str(self):
        for rec in self:
            rec.establishment_date_str = format_date(self.env, rec.establishment_date) if rec.establishment_date else ""

