from odoo import api, models
from odoo.addons.addon_restful.common import rest_api_model, rest_api_method


class RedTag(models.Model):
    _inherit = "red.tag"

    def notify_new_red_tag_created(self):
        self.ensure_one()
        self.env['slack.event'].dispatch(
            'new_red_tag_created',
            {
                'object': self,
                'channel': self.env['ir.config_parameter'].sudo().get_param(
                    'slack_red_tags.red_tags_slack_channel') or '',
                'menu': self.env.ref('red_tags.red_tag_menu').id,
                'action': self.env.ref('red_tags.red_tag_action').id,
                'button_name': 'Open red tag'
            }
        )
        return True

    def notify_red_tag_state_changes(self, new_state, user):
        self.ensure_one()
        self.env['slack.event'].dispatch(
            'red_tag_state_changes',
            {
                'object': self,
                'new_state': dict(self._fields['state'].selection).get(new_state),
                'user': user,
                'channel': self.env['ir.config_parameter'].sudo().get_param(
                    'slack_red_tags.red_tags_slack_channel') or '',
                'menu': self.env.ref('red_tags.red_tag_menu').id,
                'action': self.env.ref('red_tags.red_tag_action').id,
                'button_name': 'Open red tag'
            }
        )
        return True

    def notify_red_tag_assignee(self, assignee):
        self.ensure_one()
        self.env['slack.event'].dispatch(
            'red_tag_assignee',
            {
                'object': self,
                'user': assignee,
                'assigned_by': self.env.user.name,
                'channel': self.env['ir.config_parameter'].sudo().get_param(
                    'slack_red_tags.red_tags_slack_channel') or '',
                'menu': self.env.ref('red_tags.red_tag_menu').id,
                'action': self.env.ref('red_tags.red_tag_action').id,
                'button_name': 'Open red tag'
            }
        )
        return True

    @api.model
    @rest_api_method()
    def create(self, values):
        red_tag = super().create(values)
        red_tag.notify_new_red_tag_created()
        if 'assignee' not in values:
            pass
        elif values['assignee']:
            assignee = red_tag.env['res.users'].search([('id', '=', values['assignee'])], limit=1)
            red_tag.notify_red_tag_assignee(assignee)
        return red_tag

    def write(self, values):
        if 'state' in values.keys() and not self.activity_ids:
            self.notify_red_tag_state_changes(values['state'], self.env.user.name)
        if 'assignee' not in values:
            pass
        elif values['assignee']:
            assignee = self.env['res.users'].search([('id', '=', values['assignee'])], limit=1)
            self.notify_red_tag_assignee(assignee)
        res = super().write(values)
        return res
