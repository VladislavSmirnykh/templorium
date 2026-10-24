from odoo.tests import TransactionCase, tagged

from .field_specs import MODEL_SPECS


@tagged('post_install', '-at_install', 'templorium_demo')
class TestTemploriumDemoFieldMetadata(TransactionCase):
    """Registry-level checks: type and field definition attributes."""

    def _assert_field(self, model, field_name, spec):
        field = model._fields[field_name]
        for key, expected in spec.items():
            with self.subTest(model=model._name, field=field_name, attribute=key):
                if key == 'compute':
                    self.assertEqual(bool(field.compute), expected)
                elif key == 'default':
                    if callable(field.default):
                        rec = model.new({})
                        self.assertEqual(field.default(rec), expected)
                    else:
                        self.assertEqual(field.default, expected)
                elif key == 'attachment':
                    self.assertEqual(getattr(field, 'attachment', False), expected)
                elif key == 'definition':
                    self.assertEqual(field.definition, expected)
                elif key == 'model_field':
                    self.assertEqual(field.model_field, expected)
                elif key == 'currency_field':
                    self.assertEqual(field.currency_field, expected)
                elif key == 'comodel_name':
                    self.assertEqual(field.comodel_name, expected)
                elif key == 'related':
                    self.assertEqual(field.related, expected)
                elif key == 'copy':
                    self.assertEqual(bool(field.copy), expected)
                else:
                    self.assertEqual(getattr(field, key), expected)

    def test_showcase_and_related_models_field_definitions(self):
        for model_name, field_specs in MODEL_SPECS.items():
            model = self.env[model_name]
            for field_name, spec in field_specs.items():
                with self.subTest(model=model_name, field=field_name):
                    self.assertIn(field_name, model._fields)
                    self._assert_field(model, field_name, spec)

    def test_selection_keys_documented(self):
        showcase = self.env['templorium.demo.showcase']
        scalar = showcase._fields['scalar_selection']
        self.assertEqual(
            set(scalar.get_values(self.env)),
            {'draft', 'confirmed', 'done'},
        )
        ref_model = showcase._fields['ref_model']
        self.assertEqual(
            set(ref_model.get_values(self.env)),
            {'templorium.demo.ref.target', 'res.partner'},
        )

    def test_ir_model_fields_reflection_copied_flags(self):
        """DB metadata copied column matches registry copy for showcase scalars."""
        IrFields = self.env['ir.model.fields'].sudo()
        showcase = self.env['templorium.demo.showcase']
        for field_name, spec in MODEL_SPECS['templorium.demo.showcase'].items():
            if 'copy' not in spec:
                continue
            row = IrFields.search([
                ('model', '=', showcase._name),
                ('name', '=', field_name),
            ], limit=1)
            self.assertTrue(row, f'missing ir.model.fields for {field_name}')
            self.assertEqual(bool(row.copied), spec['copy'], field_name)
