from odoo import fields , models


class SchoolClassStudents(models.Model):
    _name='school.class.students'
    _description='School Class Students'

    student_id = fields.Many2one('school.student',string='Student')
    semester_id = fields.Many2one('school.semester',string='Semester')
    academic_year_id = fields.Many2one('school.academic.year',string='AcademicYear')
    class_id = fields.Many2one('school.class',string='Class')



