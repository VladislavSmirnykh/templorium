from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'templorium_demo')
class TestTemploriumDemoBus(TransactionCase):

    def test_action_send_bus_notification_creates_bus_row(self):
        showcase = self.env['templorium.demo.showcase'].create({
            'name': 'Bus demo',
            'scalar_boolean_required': False,
        })
        showcase.action_send_bus_notification()
        self.env.cr.flush()
        last = self.env['bus.bus'].sudo().search(
            [
                ('message', 'ilike', 'simple_notification'),
                ('message', 'ilike', showcase.name),
            ],
            order='id desc',
            limit=1,
        )
        self.assertTrue(last)
        self.assertIn('Bus bus', last.message)
