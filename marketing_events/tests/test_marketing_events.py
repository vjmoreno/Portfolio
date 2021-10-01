from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError
from psycopg2.errors import CheckViolation

@tagged('-at_install', 'post_install')
class TestMarketingEvents(TransactionCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

    def test_marketing_events(self):
        self.test_marketing_event = self.env['marketing.event'].create({'name': 'Test',
                                                                        'start_date': '2021-08-30',
                                                                        'end_date': '2021-08-31',
                                                                        'owner': self.env.user.id,
                                                                        'description': 'Test'})
        # Writing the record, the start date must be anterior to the end date.
        with self.assertRaises(ValidationError):
            self.test_marketing_event.write({'end_date': '2021-08-29'})
        # Creating the record, the start date must be anterior to the end date.
        with self.assertRaises(ValidationError):
            self.env['marketing.event'].create({'name': 'Test2',
                                                'start_date': '2021-08-31',
                                                'end_date': '2021-08-30',
                                                'owner': self.env.user.id,
                                                'description': 'Test2'})