from odoo import models, fields

class SchoolTeacher(models.Model):
    _name = 'school.teacher'
    _description = 'Teacher'
    _inherits = {'res.partner':'partner_id'}

    # name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete='cascade')
    # email = fields.Char(string='Email')
    grade_level = fields.Selection(
        [
            ('level_1', 'Grade 1'),
            ('level_2', 'Grade 2'),
        ],)

    #     string="Grade Level",
    #     default='level_1',)
    #
