from odoo import models , fields

class Semester(models.Model):
    _name = 'school.semester'

    #academic year -// name
    academic_year_id = fields.Many2one('academic.year')
    name = fields.Char(string='Name')