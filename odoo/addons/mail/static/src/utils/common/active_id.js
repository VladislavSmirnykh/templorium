/** @odoo-module **/

import { isPersistedRecordId } from "@web/model/relational_model/record_id";

/**
 * Parse a discuss/mail ``active_id`` token (e.g. ``discuss.channel_<uuid>``).
 *
 * @param {string|number|undefined} rawActiveId
 * @returns {[string, string|number]|undefined}
 */
export function parseDiscussActiveId(rawActiveId) {
    if (rawActiveId === undefined || rawActiveId === null || rawActiveId === "") {
        return undefined;
    }
    if (typeof rawActiveId === "number") {
        return ["discuss.channel", rawActiveId];
    }
    if (typeof rawActiveId !== "string") {
        return undefined;
    }
    const sep = rawActiveId.lastIndexOf("_");
    if (sep <= 0) {
        return undefined;
    }
    const model = rawActiveId.slice(0, sep);
    const idPart = rawActiveId.slice(sep + 1);
    const id = /^\d+$/.test(idPart) ? parseInt(idPart, 10) : idPart;
    return [model, id];
}

/**
 * @param {string|number|undefined} id
 * @returns {boolean}
 */
export function isPersistedDiscussRecordId(id) {
    return isPersistedRecordId(id);
}
