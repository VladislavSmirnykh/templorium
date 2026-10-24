"""Configurable SUPERUSER_ID (``base.user_root`` / login ``__system__``)."""
from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from odoo.sql_db import BaseCursor

_logger = logging.getLogger(__name__)

# Default bootstrap id in base/data/base_data.sql (odoo.orm.bootstrap_ids.USER_ROOT).
DEFAULT_SUPERUSER_ID = "00000000-0000-0000-0000-000000000001"

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def normalize_superuser_id(value: str) -> str:
    value = (value or "").strip().lower()
    if not UUID_RE.match(value):
        raise ValueError(f"Invalid superuser_id {value!r} (expected UUID)")
    return value


def get_configured_superuser_id() -> str:
    from odoo.tools import config

    raw = config.get("superuser_id") or DEFAULT_SUPERUSER_ID
    return normalize_superuser_id(raw)


def set_superuser_id(uid: str) -> None:
    """Update module-level SUPERUSER_ID used by the ORM and ``odoo.api``."""
    import odoo.api as api_mod
    import odoo.orm.utils as utils

    utils.SUPERUSER_ID = uid
    api_mod.SUPERUSER_ID = uid


def refresh_superuser_id_from_config() -> str:
    uid = get_configured_superuser_id()
    set_superuser_id(uid)
    return uid


def substitute_bootstrap_user_root(sql: str) -> str:
    configured = get_configured_superuser_id()
    if configured == DEFAULT_SUPERUSER_ID:
        return sql
    return sql.replace(DEFAULT_SUPERUSER_ID, configured)


def _foreign_key_columns_to_res_users(cr: BaseCursor) -> list[tuple[str, str]]:
    cr.execute(
        """
        SELECT cl.relname, att.attname
        FROM pg_constraint c
        JOIN pg_class cl ON cl.oid = c.conrelid
        JOIN pg_class ref ON ref.oid = c.confrelid
        JOIN pg_attribute att ON att.attrelid = c.conrelid AND att.attnum = ANY(c.conkey)
        JOIN pg_attribute refatt ON refatt.attrelid = c.confrelid
            AND refatt.attnum = ANY(c.confkey) AND refatt.attname = 'id'
        WHERE c.contype = 'f'
          AND ref.relname = 'res_users'
          AND array_length(c.confkey, 1) = 1
        """
    )
    return [(row[0], row[1]) for row in cr.fetchall()]


def sync_superuser_record_id(cr: BaseCursor) -> None:
    """Ensure ``base.user_root`` uses the UUID from ``odoo.conf`` (``superuser_id``)."""
    from odoo.tools import sql as sql_tools

    if not sql_tools.table_exists(cr, "ir_model_data"):
        return

    target_id = get_configured_superuser_id()
    cr.execute(
        """
        SELECT res_id::text
        FROM ir_model_data
        WHERE module = 'base' AND name = 'user_root' AND model = 'res.users'
        LIMIT 1
        """
    )
    row = cr.fetchone()
    if not row:
        return
    current_id = row[0]
    if current_id == target_id:
        return

    cr.execute("SELECT id::text, login FROM res_users WHERE id = %s", (current_id,))
    root_row = cr.fetchone()
    if not root_row:
        _logger.warning(
            "superuser_id sync: xmlid base.user_root points to %s but res_users row is missing",
            current_id,
        )
        return

    cr.execute("SELECT id::text, login FROM res_users WHERE id = %s", (target_id,))
    collision = cr.fetchone()
    if collision and collision[0] != current_id:
        raise RuntimeError(
            f"superuser_id={target_id!r} is already used by res.users login {collision[1]!r}; "
            f"cannot reassign base.user_root from {current_id!r}"
        )

    _logger.info(
        "Updating superuser id from %s to %s (login %r)",
        current_id,
        target_id,
        root_row[1],
    )

    cr.execute("SET session_replication_role = replica")
    try:
        cr.execute("UPDATE res_users SET id = %s WHERE id = %s", (target_id, current_id))
        for table, column in _foreign_key_columns_to_res_users(cr):
            if table == "res_users" and column == "id":
                continue
            cr.execute(
                f'UPDATE "{table}" SET "{column}" = %s WHERE "{column}" = %s',
                (target_id, current_id),
            )
        cr.execute(
            """
            UPDATE ir_model_data
            SET res_id = %s
            WHERE module = 'base' AND name = 'user_root' AND model = 'res.users'
            """,
            (target_id,),
        )
        cr.execute(
            "UPDATE ir_model_data SET res_id = %s WHERE model = 'res.users' AND res_id = %s",
            (target_id, current_id),
        )
    finally:
        cr.execute("SET session_replication_role = DEFAULT")
