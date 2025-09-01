from odoo import fields, models ,api

class SchoolEnrollment(models.Model):
    _name = 'school.enrollment'
    _description = 'School Enrollment'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'school.followers']

    name = fields.Char(string='Enrollment No.', readonly=True, copy=False, default="/", tracking=True)
    parent_id = fields.Many2one('res.partner', string='Parent')
    student_id = fields.Many2one('school.student', string='Student')
    semester_id =fields.Many2one('school.semester', string='Semester')
    academic_year_id = fields.Many2one('academic.year', string="Academic Year")
    class_id = fields.Many2one('school.class', string='Class')
    # book_level = fields.Selection([('level_1','Level 1'), ('level_2','Level 2')], string='Book Level')

    book_level = fields.Selection([
        ('level_1', 'Grade 1'),
        ('level_2', 'Grade 2')],
        string="Book Level")

    state = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled")],
        default="draft",
    )

    def action_from_draft_to_active(self):
        for rec in self:
            rec.write({'state': 'active'})

    def action_to_confirm(self):
        for rec in self:
            rec.write({'state': 'confirmed'})

    def action_to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    def action_to_completed(self):
        for rec in self:
            rec.write({'state':'completed'})

    def action_to_cancelled(self):
        for rec in self:
            rec.write({'state':'cancelled'})

    @api.model_create_multi
    def create(self, vals_list):
        seq_code = "school.enrollment.seq"
        for vals in vals_list:
            if not vals.get("name") or vals["name"] == "/":
                vals["name"] = self.env["ir.sequence"].next_by_code(seq_code) or "/"
        return super().create(vals_list)
