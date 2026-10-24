/** @odoo-module **/

import { types as t } from "@odoo/owl";

const UUID_RECORD_ID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/** @returns {boolean} whether ``id`` is a persisted database id (UUID string). */
export function isPersistedRecordId(id) {
    return typeof id === "string" && UUID_RECORD_ID_RE.test(id);
}

export const persistedRecordIdType = t.customValidator(
    t.string(),
    (id) => isPersistedRecordId(id),
    "value is not a valid record id"
);

/** Persisted record/view id, or ``false`` when absent (e.g. default view). */
export const persistedRecordIdOrFalseType = t.or([persistedRecordIdType, t.literal(false)]);
