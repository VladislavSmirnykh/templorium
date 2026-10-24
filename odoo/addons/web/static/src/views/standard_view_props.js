import { t } from "@odoo/owl";
import {
    persistedRecordIdOrFalseType,
    persistedRecordIdType,
} from "@web/model/relational_model/record_id";

export const standardViewProps = {
    info: t.object(),
    resModel: t.string(),
    arch: t.instanceOf(Element),
    className: t.string().optional(),
    context: t.object(),
    createRecord: t.function().optional(),
    display: t.object().optional(),
    domain: t.array(),
    fields: t.object(),
    globalState: t.object().optional(),
    groupBy: t.array(t.string()),
    limit: t.number().optional(),
    noBreadcrumbs: t.boolean().optional(),
    orderBy: t.array(t.object()),
    relatedModels: t.object().optional(),
    resId: persistedRecordIdOrFalseType.optional(),
    resIds: t.array(persistedRecordIdType).optional(),
    searchMenuTypes: t.array(t.string()),
    selectRecord: t.function().optional(),
    state: t.object().optional(),
    useSampleModel: t.boolean(),
    updateActionState: t.function().optional(),
};
