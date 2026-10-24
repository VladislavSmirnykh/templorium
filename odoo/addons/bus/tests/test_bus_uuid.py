import uuid
from bisect import bisect_right

from odoo.addons.bus.bus_dispatcher import ChannelTopic
from odoo.addons.bus.models.bus import channel_with_db
from odoo.addons.bus.tools.channels import (
    bus_cursor_empty,
    bus_cursor_from_values,
    bus_cursor_normalize,
    bus_notification_cursor,
    normalize_bus_channel,
)
from odoo.addons.bus.tools.notifications import fetch_bus_notifications
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'bus')
class TestBusUuid(TransactionCase):

    def test_normalize_bus_channel_stringifies_user_id(self):
        user = self.env.user
        channel = normalize_bus_channel((self.env.cr.dbname, 'res.users', user.id))
        self.assertIsInstance(channel[2], str)
        self.assertEqual(channel[2], str(user.id))

    def test_channel_with_db_matches_bus_row_channel(self):
        self.env.user._bus_send(
            'simple_notification',
            {'message': 'channel key test', 'type': 'success'},
        )
        self.env.cr.flush()
        bus = self.env['bus.bus'].sudo().search(
            [('message', 'ilike', 'channel key test')],
            limit=1,
        )
        self.assertTrue(bus)
        import json

        from odoo.addons.bus.tools.misc import tuplify

        stored = tuplify(json.loads(bus.channel))
        via = channel_with_db(self.env.cr.dbname, self.env.user)
        self.assertEqual(stored, via)

    def test_fetch_bus_notifications_returns_str_ids(self):
        self.env.user._bus_send(
            'simple_notification',
            {'message': 'fetch id type', 'type': 'success'},
        )
        self.env.cr.flush()
        channel = channel_with_db(self.env.cr.dbname, self.env.user)
        rows = fetch_bus_notifications(
            self.env.cr,
            {bus_cursor_empty(): [channel]},
        )
        notifs = rows[channel]
        self.assertTrue(notifs)
        self.assertIsInstance(notifs[-1]['id'], str)
        self.assertIn('cursor', notifs[-1])

    def test_bus_last_id_is_time_ordered_cursor(self):
        last_id = self.env['bus.bus'].sudo()._bus_last_id()
        self.assertIsInstance(last_id, str)
        self.assertIn('|', last_id)
        uuid.UUID(last_id.split('|', 1)[1])

    def test_fetch_uses_create_date_not_uuid_order(self):
        """Random UUID PK: ``id > last`` is wrong; cursor uses (create_date, id)."""
        channel = channel_with_db(self.env.cr.dbname, self.env.user)
        self.env.user._bus_send('simple_notification', {'message': 'bus-order-a', 'type': 'info'})
        self.env.cr.flush()
        first = self.env['bus.bus'].sudo().search(
            [('message', 'ilike', 'bus-order-a')],
            limit=1,
        )
        self.env.user._bus_send('simple_notification', {'message': 'bus-order-b', 'type': 'info'})
        self.env.cr.flush()
        second = self.env['bus.bus'].sudo().search(
            [('message', 'ilike', 'bus-order-b')],
            limit=1,
        )
        # Ensure the second row is newer in time but has a smaller UUID than an old table maximum.
        self.env.cr.execute(
            """
            UPDATE bus_bus SET create_date = %s + interval '1 second'
            WHERE id = %s::uuid
            """,
            (first.create_date, str(second.id)),
        )
        max_by_uuid = self.env['bus.bus'].sudo().search([], order='id desc', limit=1)
        if str(second.id) >= str(max_by_uuid.id):
            self.skipTest('need a newer row with smaller UUID than table max to regression-test')
        cursor = bus_cursor_from_values(first.create_date, first.id)
        rows = fetch_bus_notifications(self.env.cr, {cursor: [channel]})
        messages = [n['message']['payload']['message'] for n in rows[channel]]
        self.assertIn('bus-order-b', messages)

    def test_dispatch_bisect_uses_bus_cursor(self):
        """Regression: bisect raised TypeError and dropped live notifications."""
        empty = bus_cursor_empty()
        notifications = [
            {
                'id': 'ffc8525e-5ba6-4d18-ac45-6bd1bba20743',
                'cursor': f'2026-01-01 00:00:01|ffc8525e-5ba6-4d18-ac45-6bd1bba20743',
                'message': {},
            },
            {
                'id': 'ffd8525e-5ba6-4d18-ac45-6bd1bba20744',
                'cursor': f'2026-01-01 00:00:02|ffd8525e-5ba6-4d18-ac45-6bd1bba20744',
                'message': {},
            },
        ]
        topic = ChannelTopic(
            channel_with_db(self.env.cr.dbname, self.env.user),
            empty,
        )
        sort_key = topic._notification_sort_key
        idx = bisect_right(
            notifications,
            topic._last_fetched_id,
            key=sort_key,
        )
        self.assertEqual(idx, 0)
        self.assertEqual(notifications[idx:], notifications)

    def test_ir_websocket_accepts_uuid_string_last(self):
        self.env.user._bus_send('simple_notification', {'message': 'x', 'type': 'info'})
        self.env.cr.flush()
        bus_last = self.env['bus.bus'].sudo()._bus_last_id()
        normalized = self.env['ir.websocket']._normalize_bus_cursor(bus_last)
        self.assertEqual(
            normalized,
            bus_cursor_normalize(self.env.cr, bus_last),
        )
