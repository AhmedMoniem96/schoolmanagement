from odoo import fields,models,api , _
from odoo.exceptions import ValidationError
import re


class AcademicYear(models.Model):

    global _show_branches_currently_working
    _name = "academic.year"

    _inherit = ['mail.thread','mail.activity.mixin','school.followers']
    def _show_branches_currently_working(self):
        branches = self.env['school.branch'].search([('working_type', '!=', 'under_construction')]).id
        return branches.ids

    name = fields.Char(string="Academic Year",required=True)
    branch_id = fields.Many2one(
        "school.branch",
        string="Branch",
        domain=[('working_type', '!=', 'under_construction')]
    )

    # branch_id = fields.Many2many(
    #     "school.branch",
    #     string="Branch",
    #     default= _show_branches_currently_working
    # )
    @api.constrains('name')
    def _check_name_format_and_delta(self):
        pattern = re.compile(r'^\d{4}/\d{4}$')
        for rec in self:
            if not rec.name or not pattern.match(rec.name):
                raise ValidationError(_("Academic Year must be in the format YYYY/YYYY, e.g., 2023/2024."))

            start, end = rec.name.split('/')
            y1, y2 = int(start), int(end)
            if y2 - y1 != 1:
                raise ValidationError(_("Academic Year must span exactly one year (e.g., 2023/2024)."))
