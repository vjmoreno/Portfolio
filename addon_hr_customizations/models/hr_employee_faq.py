from odoo import api, models, fields
from odoo.addons.addon_restful.common import rest_api_model, rest_api_method
from logging import getLogger


_logger = getLogger(__name__)


@rest_api_model
class EmployeeFAQ(models.Model):
    _name = "hr.employee.faq"
    _rec_name = "question"

    question = fields.Text('Question')
    answer = fields.Text('Answer')
    is_published = fields.Boolean('Is Published')
    sequence = fields.Integer('Sequence')
    tags_ids = fields.Many2many('hr.employee.category', 'employee_faq_rel',string='Tags')

    @rest_api_method()
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        return super(EmployeeFAQ, self).search(args, offset=offset, limit=limit, order=order, count=count)

    @api.model
    def parse_fitler(self, filter_param):
        domain = [('is_published', '=', True)]
        if filter_param:
            try:
                tags_name = [param.strip() for param in filter_param.split(',')]
                if tags_name:
                    domain.append(('tags_ids.name', 'in', tags_name))
            except Exception:
                pass
        return domain


@rest_api_model
class HrEmployeeCategory(models.Model):
    _inherit = "hr.employee.category"

    @rest_api_method()
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        return super(HrEmployeeCategory, self).search(args, offset=offset, limit=limit, order=order, count=count)
