from odoo import models , fields

class SchoolBranchTags(models.Model):
    _name = "school.branch.tags"
    _description = "School Branch Tags"

    name = fields.Char(string="Name")
    created_by = fields.Many2one("res.users",string="Created By", default= lambda self: self.env.user ,readonly=True)
    date = fields.Date(string="Date",default=fields.Date.context_today)
    branch_id = fields.Many2one('school.branch',string="Branch")
    school_ids = fields.Many2many('school.school','school_rel','school_id','tags_id')