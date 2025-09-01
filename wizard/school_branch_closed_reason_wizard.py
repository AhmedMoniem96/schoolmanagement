from odoo import fields,models,api

class BranchClosedReasonWizard(models.TransientModel):
    _name = 'school.branch.closed.reason.wizard'
    _description = 'School Branch Close Reason Wizard'



    branch_id = fields.Many2one('school.branch', string='Branch')

    closing_reason = fields.Text(string='Closed Reason')
    opening_reason = fields.Text(string='Opening Reason')

    current_state = fields.Selection(related="branch_id.state",string="State")
    # checked_visible_field = fields.Boolean(related="branch_id.visible_field")
    checked_visible_field = fields.Boolean(string='Checked Visible Field')

    def action_confirm_closed_reason(self):
        values = {
            'branch_id': self.branch_id.id,
            'created_by': self.env.user.id,
            'date': fields.Datetime.now(),
        }
        if self.current_state == 'closed' :
            values['open_branch_reason'] = self.opening_reason
            self.checked_visible_field = True
            self.branch_id.write({
                'state': 'active',
                'opening_reason': self.opening_reason,
                'visible_field':self.checked_visible_field
            })

        elif self.current_state == 'active':
            values['close_branch_reason'] = self.closing_reason
            self.checked_visible_field = True
            self.branch_id.write({
                'state': 'closed',
                'closing_reason': self.closing_reason,
                'visible_field': self.checked_visible_field
            })

        self.env['school.branch.history'].create(values)

        # branch = self.env['school.branch'].browse(self._context.get('default_branch_id'))
        # if branch:
        #     branch.write({
        #         'state': self._context.get('target_state'),
        #         'closing_reason': self.closing_reason
        #     })



        # self.env['school.branch.history'].write(
        #     {
        #
        #         'close_branch_reason': self.closing_reason if self.target_state == 'closed' else "",
        #         'open_branch_reason': self.opening_reason if self.target_state  != 'closed' else "",
        #     }
        # )



