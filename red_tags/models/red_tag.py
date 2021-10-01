# -*- coding: utf-8 -*-
from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError
from odoo.addons.addon_restful.common import rest_api_model, rest_api_method
from dateutil.relativedelta import relativedelta
import json

STATES = [('draft', 'Draft'), ('pending_review', 'Pending Review'), ('to_save', 'To Save'),
          ('to_dispose', 'To Dispose'), ('to_sell', 'To Sell'), ('done', 'Done'), ('abandoned', 'Abandoned')]
STATES_LIST = list(list(zip(*STATES))[0])


@rest_api_model
class RedTag(models.Model):
    _name = 'red.tag'
    _rec_name = 'summary'
    _description = "Red Tag"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    summary = fields.Char('Summary', required=True)
    tagged_by = fields.Many2one('res.users', string="Tagged by", default=lambda self: self.env.user, readonly=True,
                                force_save=True)
    tagged_on = fields.Datetime(string='Tagged on', default=fields.Datetime.now())
    assignee = fields.Many2one('res.users', string="Assignee")
    description = fields.Html('Description')
    type = fields.Many2one('red.tag.item.type', string="Type", required=True)
    reason = fields.Many2one('red.tag.reason', string="Reason", required=True)
    state = fields.Selection(STATES, 'State', default='draft', readonly=True, force_save=True,
                             group_expand='_read_states')
    image_urls = fields.Text('Image URLs')
    qr_code_id = fields.Many2one('qr.code', string="QR code")

    @api.model
    def _read_states(self, *args):
        return STATES_LIST

    @api.onchange('qr_code_id')
    def onchange_qr_code_id(self):
        if self._origin.id:
            if self.qr_code_id:
                self.qr_code_id.write({'res_reference': 'red.tag,' + str(self._origin.id)})
                last_qr_code = self.env['qr.code'].search(
                    [('res_reference', '=', 'red.tag,' + str(self._origin.id)),
                     ('id', '!=', self.qr_code_id.id)])
            else:

                last_qr_code = self.env['qr.code'].search(
                    [('res_reference', '=', 'red.tag,' + str(self._origin.id))], limit=1)
            last_qr_code.res_reference = False

    @rest_api_method()
    @api.model
    def create(self, values):
        if 'image_urls' in values.keys():
            values['description'] = ''
            image_urls = values['image_urls'].split(',')
            for url in image_urls:
                values['description'] += '''
                <p>
                    <figure class="image">
                        <img src="{}">
                    </figure>
                </p>'''.format(url)
        if 'tagged_by' in values.keys():
            values['tagged_by'] = self.env['res.users'].search([('id', '=', values['tagged_by'])]).id
        res = super().create(values)
        res.message_post(body='A new Red Tag has been created {} by {}'.format(res.summary, res.env.user.name),
                         subtype='mail.mt_comment')
        if res.qr_code_id:
            res.qr_code_id.write({'res_reference': 'red.tag,' + str(res.id)})
        return res

    @rest_api_method()
    def write_red_tag(self, values):
        """
        We update the qr_code_id.res_reference here instead of
        in the write() method because it produces an infinite
        loop. We are already calling the write() method of
        this model from the write() method of  the qr.code model.
        """
        values = json.loads(values)
        if 'image_urls' in values.keys():
            values['description'] = ''
            image_urls = values['image_urls'].split(',')
            for url in image_urls:
                values['description'] += '''
                <p>
                    <figure class="image">
                        <img src="{}">
                    </figure>
                </p>'''.format(url)
        if 'qr_code_id' in values.keys():
            qr_code_id = self.env['qr.code'].search([('id', '=', values['qr_code_id'])], limit=1)
            if not values['qr_code_id']:
                self.qr_code_id.res_reference = False
            elif qr_code_id:
                self.qr_code_id.res_reference = False
                qr_code_id.res_reference = 'red.tag,{}'.format(self.id)
        self.write(values)
        return {
            'id': self.id,
            'qr_code': self.qr_code_id.qr_code,
            'qr_code_id': self.qr_code_id.id,
            'type': self.type.name,
            'reason': self.reason.name,
            'state': self.state,
            'summary': self.summary,
            'tagged_by': self.tagged_by.id,
            'assignee': self.assignee.id,
            'tagged_on': self.tagged_on,
            'image_urls': self.image_urls
        }

    @api.model
    @rest_api_method()
    def get_red_tag(self, qr_code):
        qr_code = self.env['qr.code'].search([('qr_code', '=', qr_code)], limit=1)
        if not qr_code:
            return {'message': 'QR code not found.'}
        red_tag = self.env['red.tag'].search([('qr_code_id', '=', qr_code.id)], limit=1)
        if red_tag:
            return {
                'id': red_tag.id,
                'qr_code': qr_code.qr_code,
                'qr_code_id': qr_code.id,
                'type': red_tag.type.name,
                'reason': red_tag.reason.name,
                'state': red_tag.state,
                'summary': red_tag.summary,
                'tagged_by': red_tag.tagged_by.id,
                'assignee': red_tag.assignee.id,
                'tagged_on': red_tag.tagged_on,
                'image_urls': red_tag.image_urls
            }
        else:
            return {'message': 'Red Tag not found.'}

    @rest_api_method()
    def get_item_types(self):
        item_types = self.env['red.tag.item.type'].search([])
        item_types = [{'id': item_type.id, 'name': item_type.name} for item_type in item_types]
        return item_types

    @rest_api_method()
    def get_reasons(self):
        reasons = self.env['red.tag.reason'].search([])
        reasons = [{'id': reason.id, 'name': reason.name} for reason in reasons]
        return reasons

    def action_pending_review(self):
        self.state = 'pending_review'
        self._add_planned_activities()

    def action_to_save(self):
        self.state = 'to_save'
        self._add_planned_activities()

    def action_to_dispose(self):
        self.state = 'to_dispose'
        self._add_planned_activities()

    def action_to_sell(self):
        self.state = 'to_sell'
        self._add_planned_activities()

    def action_done(self):
        self.state = 'done'
        self._add_planned_activities()

    def action_abandoned(self):
        self.state = 'abandoned'
        self._add_planned_activities()

    def unlink(self):
        for red_tag in self:
            if red_tag.state not in ['draft', 'done', 'abandoned']:
                raise UserError(
                    'You cannot delete an a red tag that is not in the following states: Draft, Done or Abandoned')
        return super(RedTag, self).unlink()

    def write(self, values):
        if 'state' not in values:
            pass
        elif values['state']:
            if values['state'] not in ['draft', 'done']:
                self.message_post(
                    body='Red tag {} has been moved from {} to {} by {}'.format(self.summary,
                                                                                dict(self._fields['state'].selection).
                                                                                get(self.state),
                                                                                dict(self._fields['state'].selection).
                                                                                get(values['state']),
                                                                                self.env.user.name),
                    subtype='mail.mt_comment')
            elif values['state'] == 'done':
                self.message_post(body='Red Tag {} has been completed. '.format(self.summary),
                                  subtype='mail.mt_comment')
        res = super().write(values)
        return res

    def _add_planned_activities(self, validate_previous_state=True):
        """
        Creates Planned Activities for a given transition state.
        @params:
            state: string with new state to add activities
            validate_previous_state: boolean to validate if there are
            any pending activities
        """
        # If any previous transition activity
        if validate_previous_state and len(self.activity_ids) > 0:
            raise ValidationError(
                'Not possible to transition to \'{}\' because there are pending transition activities.'.format(
                    dict(STATES)[self.state]))

        for activity in self.env["red.tag.transition.activity"].search([('state', '=', self.state)]):
            activity_vals = {
                "activity_type_id": activity.activity_type_id.id,
                "summary": activity.summary,
                "note": activity.description,
                "date_deadline": fields.Date.context_today(self) + relativedelta(days=activity.due_days),
                "supervisor_user_id": activity.supervisor_user_id and activity.supervisor_user_id.id or False,
                "user_id": activity.user_id and activity.user_id.id or self.env.user.id,
                "res_model_id": self.env["ir.model"].search([("model", "=", self._name)], limit=1).id,
                "res_id": self.id,
                "automated": True,
            }
            self.env["mail.activity"].sudo().create(activity_vals)
