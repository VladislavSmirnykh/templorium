import { registry } from "@web/core/registry";
import { booleanField } from "@web/views/fields/boolean/boolean_field";

/** Legacy widget name: behaves as a normal boolean (no enterprise upsell). */
registry.category("fields").add("upgrade_boolean", { ...booleanField });
