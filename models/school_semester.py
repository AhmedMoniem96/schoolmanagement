from odoo import fields,models

class SchoolSemester(models.Model):
    _name = 'school.semester'
    _description = 'School Semester'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'school.followers']
    name = fields.Char('Semester Name', required=True)
    academic_year_id =fields.Many2one('academic.year', string='Academic Year')
