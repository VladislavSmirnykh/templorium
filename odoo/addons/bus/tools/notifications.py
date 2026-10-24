import json
from collections import defaultdict

from odoo.tools import SQL, json_default

from .channels import (
    bus_cursor_from_values,
    bus_cursor_id,
    bus_cursor_min,
    bus_cursor_normalize,
    bus_cursor_parse,
    bus_notification_id,
    normalize_bus_channel,
)
from . import orjson
from .misc import tuplify


def json_dump(v):
    return json.dumps(v, separators=(",", ":"), default=json_default)


def fetch_bus_notifications(cr, channels_by_last_fetched_id, ignore_ids=None):
    """Fetch notifications from the bus table.

    :param cr: Database cursor.
    :param channels_by_last_fetched_id: Channels grouped by their last fetched
        cursor, the lower bound for their notifications.
    :param ignore_ids: IDs to exclude.
    :return: Notifications grouped by channel, each group sorted by cursor.

    """
    last_fetched_id_by_channel = {}
    for last_fetched_id, channels in channels_by_last_fetched_id.items():
        last_fetched_id = bus_cursor_normalize(cr, last_fetched_id)
        for channel in channels:
            json_channel = json_dump(normalize_bus_channel(channel))
            last_fetched_id_by_channel[json_channel] = bus_cursor_min(
                last_fetched_id_by_channel.get(json_channel, last_fetched_id),
                last_fetched_id,
            )
    if not last_fetched_id_by_channel:
        return {}
    values = SQL(", ").join(
        SQL(
            "(%s, %s::timestamp, %s::uuid)",
            json_channel,
            bus_cursor_parse(last_fetched_id)[0],
            bus_cursor_parse(last_fetched_id)[1],
        )
        for json_channel, last_fetched_id in last_fetched_id_by_channel.items()
    )
    query = SQL(
        """
        SELECT b.id, b.message, b.channel, b.create_date
        FROM bus_bus b
        JOIN (VALUES %s) AS v(channel, last_create_date, last_fetched_id)
          ON b.channel = v.channel
         AND (b.create_date, b.id) > (v.last_create_date, v.last_fetched_id)
        """,
        values,
    )
    if ignore_ids:
        query = SQL(
            "%s AND b.id NOT IN %s",
            query,
            tuple({bus_cursor_id(notif_id) for notif_id in ignore_ids}),
        )
    cr.execute(SQL("%s ORDER BY b.create_date, b.id", query))
    notifications_by_channel = defaultdict(list)
    for notif_id, message, channel, create_date in cr.fetchall():
        bus_channel = normalize_bus_channel(tuplify(orjson.loads(channel)))
        notif_id = bus_notification_id(notif_id)
        notifications_by_channel[bus_channel].append(
            {
                'id': notif_id,
                'cursor': bus_cursor_from_values(create_date, notif_id),
                'message': orjson.loads(message),
            },
        )
    return notifications_by_channel
