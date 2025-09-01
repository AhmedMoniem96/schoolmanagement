from odoo import models , fields , _ , api
from odoo.exceptions import UserError

class SchoolClass(models.Model):
    _name = 'school.class'
    _description = 'School Class'

    #name , semester_id , academic_year_id
    name = fields.Char(string='Name')
    semester_id = fields.Many2one('school.semester')
    academic_year_id = fields.Many2one('academic.year')
    book_level=fields.Selection([
        ('level_1','Level 1'),
        ('level_2','Level 2'),
       ],required=True)
    student_ids =fields.One2many('school.student','class_id',string="Students Enrolled")

    certificate_ids = fields.Many2many(
        'ir.attachment',
        'school_class_certificate_rel',
        'class_id', 'attachment_id',
        string='Certificates')

    school_id = fields.Many2one('school.school', string='School', ondelete='cascade')
    teacher_id = fields.Many2one('school.teacher', string='Teacher')
    state = fields.Selection(
        [('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active')],
        string='Status',
        default='draft',
        tracking=True,
    )
    teacher_id = fields.Many2one('school.teacher', string='Teacher')

    def action_confirm(self):
        for rec in self:
            if rec.state != 'draft':
                continue
            if not rec.certificate_ids:
                raise UserError(_("Attach at least one certificate before confirming."))
            rec.state = 'confirmed'
        return True

    def action_set_active(self):
        for rec in self:
            if rec.state == 'confirmed':
                rec.state = 'active'
        return True
