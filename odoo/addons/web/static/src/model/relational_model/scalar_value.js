/** @odoo-module **/

/**
 * Unset scalar in the client model (matches server NULL / Python None only).
 *
 * @param {any} value
 * @returns {boolean}
 */
export function isUnsetScalar(value) {
    return value === null || value === undefined;
}

/**
 * Unset boolean (distinct from explicit `false`).
 *
 * @param {any} value
 * @returns {boolean}
 */
export function isUnsetBoolean(value) {
    return value === null || value === undefined;
}

/**
 * @param {any} value
 * @returns {boolean}
 */
export function isEmptyScalarForDisplay(value) {
    return isUnsetScalar(value);
}
