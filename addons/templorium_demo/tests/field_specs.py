# Expected registry attributes for demo models (business fields only).

SHOWCASE_FIELD_SPECS = {
    'name': {
        'type': 'char', 'required': True, 'readonly': False, 'store': True, 'copy': True,
    },
    'active': {
        'type': 'boolean', 'required': False, 'store': True, 'copy': True, 'default': True,
    },
    'notes': {'type': 'text', 'store': True, 'copy': True},
    'scalar_char_optional': {'type': 'char', 'store': True, 'copy': True},
    'scalar_html': {'type': 'html', 'store': True, 'copy': True},
    'scalar_integer': {'type': 'integer', 'store': True, 'copy': True},
    'scalar_big_integer': {'type': 'big_integer', 'store': True, 'copy': True},
    'scalar_float': {'type': 'float', 'store': True, 'copy': True},
    'scalar_decimal': {'type': 'decimal', 'store': True, 'copy': True},
    'scalar_monetary': {
        'type': 'monetary', 'store': True, 'copy': True, 'currency_field': 'currency_id',
    },
    'currency_id': {
        'type': 'many2one', 'store': True, 'copy': True, 'comodel_name': 'res.currency',
    },
    'scalar_boolean_required': {
        'type': 'boolean', 'required': True, 'store': True, 'copy': True,
    },
    'scalar_boolean_nullable': {'type': 'boolean', 'store': True, 'copy': True},
    'scalar_selection': {'type': 'selection', 'store': True, 'copy': True},
    'scalar_date': {'type': 'date', 'store': True, 'copy': True},
    'scalar_datetime': {'type': 'datetime', 'store': True, 'copy': True},
    'scalar_binary': {'type': 'binary', 'store': True, 'copy': True, 'attachment': True},
    'scalar_binary_filename': {'type': 'char', 'store': True, 'copy': True},
    'scalar_image': {'type': 'binary', 'store': True, 'copy': True},
    'scalar_json': {'type': 'json', 'store': True, 'copy': True},
    'kanban_stage': {'type': 'selection', 'required': True, 'store': True, 'copy': True},
    'rel_partner_id': {
        'type': 'many2one', 'store': True, 'copy': True, 'comodel_name': 'res.partner',
    },
    'rel_tag_ids': {
        'type': 'many2many', 'store': True, 'copy': True, 'comodel_name': 'templorium.demo.tag',
    },
    'rel_line_ids': {
        'type': 'one2many', 'store': True, 'copy': False, 'comodel_name': 'templorium.demo.line',
    },
    'ref_model': {'type': 'selection', 'store': True, 'copy': True},
    'ref_id': {'type': 'many2one_reference', 'store': True, 'copy': True, 'model_field': 'ref_model'},
    'ref_classic': {'type': 'reference', 'store': True, 'copy': True},
    'properties_schema_id': {
        'type': 'many2one', 'store': True, 'copy': True,
        'comodel_name': 'templorium.demo.properties.schema',
    },
    'dynamic_properties': {
        'type': 'properties', 'store': True, 'copy': True,
        'definition': 'properties_schema_id.properties_definition',
    },
    'related_partner_email': {
        'type': 'char', 'related': 'rel_partner_id.email', 'readonly': False, 'store': False, 'copy': False,
    },
    'compute_operand_a': {'type': 'integer', 'store': True, 'copy': True},
    'compute_operand_b': {'type': 'integer', 'store': True, 'copy': True},
    'compute_sum_stored': {
        'type': 'integer', 'store': True, 'copy': False, 'compute': True, 'readonly': True,
    },
    'compute_label_preview': {
        'type': 'char', 'store': False, 'copy': False, 'compute': True, 'readonly': True,
    },
    'onchange_quantity': {'type': 'float', 'store': True, 'copy': True},
    'onchange_unit_price': {'type': 'float', 'store': True, 'copy': True},
    'onchange_hint': {'type': 'char', 'store': True, 'copy': True, 'readonly': False},
    'constraint_min_name_len': {'type': 'integer', 'store': True, 'copy': True},
}

LINE_FIELD_SPECS = {
    'showcase_id': {
        'type': 'many2one', 'required': True, 'store': True, 'copy': True,
        'comodel_name': 'templorium.demo.showcase',
    },
    'sequence': {'type': 'integer', 'store': True, 'copy': True, 'default': 10},
    'name': {'type': 'char', 'required': True, 'store': True, 'copy': True},
    'quantity': {'type': 'float', 'store': True, 'copy': True},
    'unit_price': {
        'type': 'monetary', 'store': True, 'copy': True, 'currency_field': 'currency_id',
    },
    'currency_id': {
        'type': 'many2one', 'related': 'showcase_id.currency_id', 'store': False, 'copy': False,
        'comodel_name': 'res.currency',
    },
    'line_total': {
        'type': 'monetary', 'store': True, 'copy': False, 'compute': True, 'readonly': True,
        'currency_field': 'currency_id',
    },
}

TAG_FIELD_SPECS = {
    'name': {'type': 'char', 'required': True, 'store': True, 'copy': True},
    'color': {'type': 'integer', 'store': True, 'copy': True},
}

REF_TARGET_FIELD_SPECS = {
    'name': {'type': 'char', 'required': True, 'store': True, 'copy': True},
    'note': {'type': 'text', 'store': True, 'copy': True},
}

PROPERTIES_SCHEMA_FIELD_SPECS = {
    'name': {'type': 'char', 'required': True, 'store': True, 'copy': True},
    'properties_definition': {'type': 'properties_definition', 'store': True, 'copy': True},
}

MODEL_SPECS = {
    'templorium.demo.showcase': SHOWCASE_FIELD_SPECS,
    'templorium.demo.line': LINE_FIELD_SPECS,
    'templorium.demo.tag': TAG_FIELD_SPECS,
    'templorium.demo.ref.target': REF_TARGET_FIELD_SPECS,
    'templorium.demo.properties.schema': PROPERTIES_SCHEMA_FIELD_SPECS,
}
