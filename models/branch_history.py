from odoo import fields,models

class SchoolBranchHistory(models.Model):
    _name = "school.branch.history"
    _description = 'School Branch History'

    branch_id = fields.Many2one("school.branch" , string="Branches" , required=True)
    created_by = fields.Many2one("res.users" , string="Created By" , required=True)
    date = fields.Datetime(string='Date',required=True, default=fields.Datetime.now)
    close_branch_reason = fields.Char(string='Close Reason')
    open_branch_reason = fields.Char(string='Re_open Reason')

