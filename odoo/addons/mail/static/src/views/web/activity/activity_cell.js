import { ActivityListPopover } from "@mail/core/web/activity_list_popover";
import { Avatar } from "@mail/views/web/fields/avatar/avatar";

import { Component, signal, t, useProps } from "@odoo/owl";

import { usePopover } from "@web/core/popover/popover_hook";

import { formatDate } from "@web/core/l10n/dates";
import { _t } from "@web/core/l10n/translation";
import { formatList } from "@web/core/l10n/utils";
import { persistedRecordIdType } from "@web/model/relational_model/record_id";

export class ActivityCell extends Component {
    static components = {
        Avatar,
    };
    static template = "mail.ActivityCell";

    contentRef = signal.ref();

    setup() {
        this.props = useProps({
            activityIds: t.array(persistedRecordIdType),
            activityTypeId: persistedRecordIdType,
            attachmentsInfo: t
                .object({
                    count: t.number(),
                    most_recent_id: persistedRecordIdType,
                    most_recent_name: t.string(),
                })
                .optional(),
            countByState: t.record(t.number()),
            reloadFunc: t.function([]),
            reportingDate: t.string(),
            resId: persistedRecordIdType,
            resModel: t.string(),
            summaries: t.array(),
            userAssignedIds: t.array(persistedRecordIdType),
            roleToAssignIds: t.array(persistedRecordIdType).optional(),
        });
        this.popover = usePopover(ActivityListPopover, { position: "bottom-start" });
    }

    get reportingDateFormatted() {
        return formatDate(luxon.DateTime.fromISO(this.props.reportingDate));
    }
    get displayedSummaries() {
        const summariesWithContent = this.props.summaries.filter((textContent) => !!textContent);
        const extras = this.props.summaries.length - summariesWithContent.length;
        if (summariesWithContent.length > 0 && extras > 0) {
            summariesWithContent.push(_t("%(extraCount)s more", { extraCount: extras }));
        }
        return formatList(summariesWithContent);
    }

    get ongoingActivityCount() {
        return (
            (this.props.countByState?.planned ?? 0) +
            (this.props.countByState?.today ?? 0) +
            (this.props.countByState?.overdue ?? 0)
        );
    }

    get totalActivityCount() {
        return this.ongoingActivityCount + (this.props.countByState?.done ?? 0);
    }

    onClick() {
        if (this.popover.isOpen) {
            this.popover.close();
        } else {
            this.popover.open(this.contentRef(), {
                activityIds: this.props.activityIds,
                defaultActivityTypeId: this.props.activityTypeId,
                onActivityChanged: () => {
                    this.props.reloadFunc();
                    this.popover.close();
                },
                resId: this.props.resId,
                resModel: this.props.resModel,
            });
        }
    }
}
