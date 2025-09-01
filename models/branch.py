from odoo import models,fields,api
from odoo.exceptions import UserError



class Branch(models.Model):
    _name= 'school.branch'
    _description = 'School Branch'
    _inherit = ['mail.thread','mail.activity.mixin','school.followers']
    name = fields.Char(string="Branch",required=True, translate=True)
    city_id = fields.Many2one("res.country.state", string="City",domain="[('country_id', '=', country_id)]")
    country_id = fields.Many2one("res.country", string="Country")
    school_id = fields.Many2one('school.school', string='School', ondelete='cascade', required=True)
    academic_years = fields.One2many('academic.year','branch_id',string="Academic year")
    user_id = fields.Many2one("res.users",default=lambda self: self.env.uid,string="User")
    working_type = fields.Selection([
        ('under_construction','Under Construction'),
        ('working',' Working'),
    ], string="Working type", default="under_construction")
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('closed', 'Closed'),
        ], default="draft"
    )
    visible_field = fields.Boolean(string='Invisible Field')
    closing_reason = fields.Text(string="Closing Reason",readonly=True)
    opening_reason = fields.Text(string="Active Reason",readonly=True)
    branch_history = fields.One2many('school.branch.history', 'branch_id', string='Branch History')

    supervisors_ids = fields.One2many('school.branch.supervisors','branch_id', string='Supervisors')
##############################model name ,      DB Relation table              pkey          pk
    tags_ids = fields.Many2many('school.branch.tags','school_branch_tags_rel','branch_id','tags_id',string="Tags",domain="[('branch_id','=',id)]")


    def add_supervisors_to_branch(self):
        all_users_existing_in_group_supervisor= self.env.ref('app1.group_supervisor').users
        # print(all_users_existing_in_group_supervisor)
        vals = self._prepare_user_supervisors(all_users_existing_in_group_supervisor)
        supervisors_ids_create = self.env['school.branch.supervisors'].create(vals)
        self.supervisors_ids = [(6,0,supervisors_ids_create.ids)]


    def _prepare_user_supervisors(self,users):
        vals = []

        for user in users:
            user_data={
                'user_id':user.id
                # 'date': fields.Datetime.now()
            }
            vals.append(user_data)
        return vals




    def action_change_state_to_draft(self):
        for rec in self:
          rec.state = 'draft'
          rec.visible_field = False
    def action_change_state_to_active(self):
        for rec in self:
          rec.state = 'active'
          rec.visible_field = False

    def action_action_open_close_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Branch Action',
            'res_model': 'school.branch.closed.reason.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_update_closed_flag(self):
        for rec in self:
            rec.visible_field = True

    @api.model_create_multi
    def create(self, vals):
        records = super(Branch,self).create(vals)
        all_users = self.env['res.users'].search([('id','!=',self.env.user.id)])
        all_internel_users_without_current_user = self.env.ref('base.group_user').users.filtered(lambda u: u.id != self.env.user.id)
        print(all_internel_users_without_current_user)
        return records


    @api.ondelete(at_uninstall=False)
    def _unlink_not_active(self):
       if self.state == 'active':
           raise UserError("cannot delete active Branch")





    # /////////////////////////////////

    def action_add_my_branch_tags(self):
        tags = self.env['school.branch.tags'].search([('branch_id', '=', self.id)])

        if tags:
            self.tags_ids = [(4, tag.id) for tag in tags]

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Added {len(tags)} tags to this branch!',
                'type': 'success',
            },
        }

    def action_remove_my_branch_tags(self):
        tags = self.env['school.branch.tags'].search([('branch_id', '=', self.id)])

        if tags:
            self.tags_ids = [(3, tag.id) for tag in tags]

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Removed {len(tags)} tags from this branch!',
                'type': 'success',
            },
        }

    def action_add_supervisors(self):
        supervisor_users = self.env['res.users'].search([]).filtered(
            lambda u: u.has_group('schoolmanagement.group_supervisor')
        )

        if not supervisor_users:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'No supervisor users found!',
                    'type': 'info',
                },
            }

        existing_supervisors = self.supervisors_ids.mapped('user_id.id')
        new_supervisors = []

        for user in supervisor_users:
            if user.id not in existing_supervisors:
                new_supervisors.append({
                    'branch_id': self.id,
                    'user_id': user.id,
                })

        if new_supervisors:
            self.env['school.branch.supervisors'].create(new_supervisors)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Added {len(new_supervisors)} supervisors!',
                'type': 'success',
            },
        }

    def action_remove_supervisors(self):
        supervisor_users = self.env['res.users'].search([]).filtered(
            lambda u: u.has_group('schoolmanagement.group_supervisor')
        )

        lines_to_remove = self.supervisors_ids.filtered(
            lambda line: line.user_id in supervisor_users
        )

        if lines_to_remove:
            lines_to_remove.unlink()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': f'Removed {len(lines_to_remove)} supervisors!',
                'type': 'success',
            },
        }
