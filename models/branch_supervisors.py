from odoo import models,fields

class BranchSupervisors(models.Model):
    _name = "school.branch.supervisors"

    branch_id = fields.Many2one("school.branch" , string="Branch")
    user_id = fields.Many2one("res.users" , string="User")
    supervisors_ids = fields.One2many('school.branch.supervisors', 'branch_id', string='Supervisors')
