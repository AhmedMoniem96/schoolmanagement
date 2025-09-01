from odoo import models,fields

class Follower(models.AbstractModel):
    _name = 'school.followers'
    _description = 'Add higher- users as followers'

    def action_add_followers(self):

        owners = self.env['res.users'].search([]).filtered(
            lambda u: u.has_group('schoolmanagement.group_owner')
        )

        head_teachers = self.env['res.users'].search([]).filtered(
            lambda u: u.has_group('schoolmanagement.group_head_teacher')
        )

        supervisors = self.env['res.users'].search([]).filtered(
            lambda u: u.has_group('schoolmanagement.group_supervisor')
        )

        student_affairs = self.env['res.users'].search([]).filtered(
            lambda u: u.has_group('schoolmanagement.group_student_affairs')
        )

        current_user = self.env.user
        users_to_add = []

        if current_user.has_group('schoolmanagement.group_teacher'):
            users_to_add = owners + head_teachers + supervisors + student_affairs

        elif current_user.has_group('schoolmanagement.group_student_affairs'):
            users_to_add = owners + head_teachers + supervisors

        elif current_user.has_group('schoolmanagement.group_supervisor'):
            users_to_add = owners + head_teachers

        elif current_user.has_group('schoolmanagement.group_head_teacher'):
            users_to_add = owners

        if users_to_add:
            partner_ids = [user.partner_id.id for user in users_to_add if user.partner_id]
            self.message_subscribe(partner_ids=partner_ids)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'Added {len(partner_ids)} higher-level users as followers!',
                    'type': 'success',
                }
            }
