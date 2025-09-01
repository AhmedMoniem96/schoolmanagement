from odoo import fields,models ,_
from odoo.exceptions import UserError

class SchoolStudent(models.Model):
    _name = 'school.student'
    _description = 'School Student'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'school.followers']
    name = fields.Char('Student Name', required=True)
    # academic_year_ids =fields.One2many('academic.year','',string='Academic Year')
    parent_id = fields.Many2one('res.partner', string='Parent')
    date_of_birth = fields.Date('Date of Birth')
    national_id = fields.Char('National ID')
    student_code = fields.Char('Student Code')
    grade = fields.Selection([
        ('grade_1','Grade 1'),
        ('grade_2','Grade 2'),
        ('grade_3','Grade 3'),],
        required=True,string="Grade")
    class_id=fields.Many2one('school.class',string='Class Enrolled')
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'school_student_attachment_rel',
        'student_id', 'attachment_id',
        string='Attachments',
        required=True
    )

    def action_confirm(self):
        for rec in self:
            if rec.state != 'draft':
                continue
            if not rec.attachment_ids:
                raise UserError(_("Attach at least one document before confirming the student."))
            rec.state = 'confirmed'
        return True

    def action_set_active(self):
        for rec in self:
            if rec.state == 'confirmed':
                rec.state = 'active'
        return True
