# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime

BUS_CURSOR_SEP = '|'
BUS_LAST_ID_EMPTY = '00000000-0000-0000-0000-000000000000'


def bus_channel_record_id(record_id):
    if record_id is None or record_id is False:
        return record_id
    return str(record_id)


def normalize_bus_channel(channel):
    """Record ids in channel tuples must be strings (JSON/NOTIFY vs ORM UUID)."""
    if not isinstance(channel, tuple):
        return channel
    if len(channel) == 3:
        dbname, name, rid = channel
        return (dbname, name, bus_channel_record_id(rid))
    if len(channel) == 4:
        dbname, name, rid, sub = channel
        return (dbname, name, bus_channel_record_id(rid), sub)
    return channel


def bus_notification_id(value):
    """Normalize ``bus.bus`` row ids for comparisons (ORM UUID vs SQL str)."""
    if value is None or value is False:
        return value
    return str(value)


def _format_create_date(create_date):
    if create_date is None:
        return '1970-01-01 00:00:00'
    if isinstance(create_date, str):
        return create_date
    text = create_date.strftime('%Y-%m-%d %H:%M:%S')
    if create_date.microsecond:
        text = f'{text}.{create_date.microsecond:06d}'
    return text


def bus_cursor_empty():
    return f'{_format_create_date(None)}|{BUS_LAST_ID_EMPTY}'


def bus_cursor_is_empty(cursor):
    if cursor is None or cursor is False:
        return True
    if cursor == BUS_LAST_ID_EMPTY:
        return True
    return cursor == bus_cursor_empty()


def bus_cursor_from_values(create_date, notif_id):
    return f'{_format_create_date(create_date)}|{bus_notification_id(notif_id)}'


def bus_cursor_id(cursor):
    if cursor is None or cursor is False:
        return BUS_LAST_ID_EMPTY
    text = str(cursor)
    if BUS_CURSOR_SEP in text:
        return bus_notification_id(text.split(BUS_CURSOR_SEP, 1)[1])
    return bus_notification_id(text)


def bus_cursor_parse(cursor):
    if bus_cursor_is_empty(cursor):
        return (_format_create_date(None), BUS_LAST_ID_EMPTY)
    text = str(cursor)
    if BUS_CURSOR_SEP in text:
        create_date, notif_id = text.split(BUS_CURSOR_SEP, 1)
        return (create_date, bus_notification_id(notif_id))
    return (None, bus_notification_id(text))


def _cursor_sort_key(cursor):
    create_date, notif_id = bus_cursor_parse(cursor)
    if create_date is None:
        create_date = '1970-01-01 00:00:00'
    return (create_date, notif_id)


def bus_cursor_lt(a, b):
    return _cursor_sort_key(a) < _cursor_sort_key(b)


def bus_cursor_gt(a, b):
    return _cursor_sort_key(a) > _cursor_sort_key(b)


def bus_cursor_min(a, b):
    if bus_cursor_is_empty(a):
        return b
    if bus_cursor_is_empty(b):
        return a
    return a if bus_cursor_lt(a, b) else b


def bus_cursor_max(a, b):
    if bus_cursor_is_empty(a):
        return b
    if bus_cursor_is_empty(b):
        return a
    return a if bus_cursor_gt(a, b) else b


def bus_cursor_normalize(cr, cursor):
    """Return a canonical ``create_date|uuid`` cursor (Templorium random UUID PKs)."""
    if bus_cursor_is_empty(cursor):
        return bus_cursor_empty()
    text = str(cursor)
    if BUS_CURSOR_SEP in text:
        create_date, notif_id = text.split(BUS_CURSOR_SEP, 1)
        return bus_cursor_from_values(create_date, notif_id)
    notif_id = bus_notification_id(text)
    cr.execute('SELECT create_date FROM bus_bus WHERE id = %s::uuid', (notif_id,))
    row = cr.fetchone()
    create_date = row[0] if row else datetime.datetime(1970, 1, 1)
    return bus_cursor_from_values(create_date, notif_id)


def bus_notification_cursor(notif):
    if notif.get('cursor'):
        return notif['cursor']
    return bus_cursor_from_values(notif.get('create_date'), notif['id'])
