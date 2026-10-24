import base64

from odoo.exceptions import ValidationError
from odoo.tests import Form, TransactionCase, tagged


@tagged('post_install', '-at_install', 'templorium_demo')
class TestTemploriumDemoFieldBehavior(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Showcase = cls.env['templorium.demo.showcase']
        cls.Tag = cls.env['templorium.demo.tag']
        cls.RefTarget = cls.env['templorium.demo.ref.target']
        cls.partner = cls.env['res.partner'].create({'name': 'Demo Partner', 'email': 'demo@example.com'})
        cls.tag_a = cls.Tag.create({'name': 'Tag A', 'color': 1})
        cls.ref_target = cls.RefTarget.create({'name': 'Ref target', 'note': 'note'})
        cls.schema = cls.env.ref('templorium_demo.demo_properties_schema_default')

    def _create_showcase(self, **extra):
        vals = {
            'name': 'Showcase record',
            'scalar_boolean_required': False,
            **extra,
        }
        return self.Showcase.create(vals)

    # --- Scalars / NULL semantics ---

    def test_create_required_and_defaults(self):
        rec = self._create_showcase()
        self.assertTrue(rec.active)
        self.assertEqual(rec.kanban_stage, 'new')
        self.assertEqual(rec.properties_schema_id, self.schema)

    def test_null_scalars_roundtrip(self):
        rec = self._create_showcase()
        rec.write({
            'scalar_char_optional': None,
            'scalar_integer': None,
            'scalar_float': None,
            'scalar_big_integer': None,
            'scalar_decimal': None,
            'scalar_selection': None,
            'scalar_date': None,
            'scalar_datetime': None,
            'scalar_json': None,
            'scalar_boolean_nullable': None,
        })
        rec.invalidate_recordset()
        read = rec.read([
            'scalar_char_optional', 'scalar_integer', 'scalar_float',
            'scalar_big_integer', 'scalar_decimal', 'scalar_selection',
            'scalar_date', 'scalar_datetime', 'scalar_json', 'scalar_boolean_nullable',
        ])[0]
        for key, val in read.items():
            if key == 'id':
                continue
            self.assertIsNone(val, key)

    def test_selection_clear_false(self):
        rec = self._create_showcase(scalar_selection='draft', ref_model='res.partner')
        rec.write({'scalar_selection': False, 'ref_model': False})
        rec.invalidate_recordset()
        self.assertIsNone(rec.scalar_selection)
        self.assertIsNone(rec.ref_model)

    def test_html_and_text(self):
        rec = self._create_showcase(notes='Line1\nLine2', scalar_html='<p>Hi</p>')
        self.assertEqual(rec.notes, 'Line1\nLine2')
        self.assertIn('Hi', rec.scalar_html)

    def test_monetary_and_currency(self):
        rec = self._create_showcase(scalar_monetary=42.5)
        self.assertEqual(rec.currency_id, self.env.company.currency_id)
        self.assertEqual(rec.scalar_monetary, 42.5)

    def test_binary_and_image_null(self):
        rec = self._create_showcase()
        rec.write({
            'scalar_binary': False,
            'scalar_image': False,
        })
        rec.invalidate_recordset()
        data = rec.read(['scalar_binary', 'scalar_image'])[0]
        self.assertIsNone(data['scalar_binary'])
        self.assertIsNone(data['scalar_image'])

    def test_binary_payload(self):
        payload = base64.b64encode(b'hello').decode()
        rec = self._create_showcase(
            scalar_binary=payload,
            scalar_binary_filename='hello.txt',
        )
        self.assertTrue(rec.scalar_binary)

    def test_json_value(self):
        rec = self._create_showcase(scalar_json={'a': 1, 'b': [2]})
        self.assertEqual(rec.scalar_json, {'a': 1, 'b': [2]})

    # --- Relational ---

    def test_demo_tag_quick_create_has_color(self):
        tag_id, _display = self.Tag.name_create('Quick tag')
        tag = self.Tag.browse(tag_id)
        self.assertGreaterEqual(tag.color, 1)
        self.assertLessEqual(tag.color, 11)

    def test_many2one_many2many(self):
        rec = self._create_showcase(
            rel_partner_id=self.partner.id,
            rel_tag_ids=[(6, 0, self.tag_a.ids)],
        )
        self.assertEqual(rec.rel_partner_id, self.partner)
        self.assertEqual(rec.rel_tag_ids, self.tag_a)

    def test_related_read_write(self):
        rec = self._create_showcase(rel_partner_id=self.partner.id)
        rec.related_partner_email = 'changed@example.com'
        self.assertEqual(rec.rel_partner_id.email, 'changed@example.com')

    def test_one2many_line_stored_compute(self):
        rec = self._create_showcase()
        rec.write({
            'rel_line_ids': [(0, 0, {
                'name': 'Line',
                'quantity': 2,
                'unit_price': 10,
            })],
        })
        line = rec.rel_line_ids
        self.assertEqual(len(line), 1)
        self.assertEqual(line.line_total, 20.0)
        line.quantity = 3
        self.assertEqual(line.line_total, 30.0)

    def test_ref_classic_legacy_false_string(self):
        """Varchar 'False' without comma must not crash read (cleared Reference)."""
        rec = self._create_showcase()
        self.env.cr.execute(
            "UPDATE templorium_demo_showcase SET ref_classic = %s WHERE id = %s",
            ('False', rec.id),
        )
        rec.invalidate_recordset(['ref_classic'])
        self.assertIsNone(rec.ref_classic)
        data = rec.read(['ref_classic'])[0]['ref_classic']
        self.assertIsNone(data)

    def test_decimal_string_roundtrip(self):
        rec = self._create_showcase(scalar_decimal='1.234567890123456789')
        rec.invalidate_recordset(['scalar_decimal'])
        self.assertEqual(
            rec.read(['scalar_decimal'])[0]['scalar_decimal'],
            '1.234567890123456789',
        )

    def test_decimal_user_literal_preserved_on_read(self):
        rec = self._create_showcase(scalar_decimal='2.2222222222222221')
        self.assertEqual(
            rec.read(['scalar_decimal'])[0]['scalar_decimal'],
            '2.2222222222222221',
        )

    def test_big_integer_int64_max(self):
        rec = self._create_showcase(scalar_big_integer=9223372036854775807)
        self.assertEqual(rec.scalar_big_integer, 9223372036854775807)

    def test_big_integer_read_as_string_for_web(self):
        rec = self._create_showcase(scalar_big_integer=9223372036854775807)
        read_val = rec.read(['scalar_big_integer'])[0]['scalar_big_integer']
        self.assertEqual(read_val, '9223372036854775807')
        rec.scalar_big_integer = 42
        self.assertEqual(rec.read(['scalar_big_integer'])[0]['scalar_big_integer'], 42)

    def test_reference_and_many2one_reference(self):
        rec = self._create_showcase()
        rec.write({
            'ref_model': 'templorium.demo.ref.target',
            'ref_id': self.ref_target.id,
            'ref_classic': f'templorium.demo.ref.target,{self.ref_target.id}',
        })
        self.assertEqual(rec.ref_id, self.ref_target.id)
        self.assertEqual(rec.ref_classic, self.ref_target)

    # --- Compute / onchange / constraint ---

    def test_stored_compute(self):
        rec = self._create_showcase(compute_operand_a=10, compute_operand_b=32)
        self.assertEqual(rec.compute_sum_stored, 42)
        rec.compute_operand_b = 5
        self.assertEqual(rec.compute_sum_stored, 15)

    def test_non_stored_compute(self):
        rec = self._create_showcase(name='Hello')
        self.assertIn('Hello', rec.compute_label_preview)

    def test_onchange_hint(self):
        with Form(self.Showcase) as form:
            form.name = 'Onchange test'
            form.scalar_boolean_required = False
            form.onchange_quantity = 4
            form.onchange_unit_price = 2.5
            self.assertIn('10', form.onchange_hint)

    def test_constraint_min_name_length(self):
        rec = self._create_showcase(constraint_min_name_len=5)
        with self.assertRaises(ValidationError):
            rec.write({'name': 'abc'})

    # --- Properties ---

    def test_properties_from_schema(self):
        rec = self._create_showcase(properties_schema_id=self.schema.id)
        props = list(rec.read(['dynamic_properties'])[0]['dynamic_properties'])
        for prop in props:
            if prop['name'] == 'demo_prop_char':
                prop['value'] = 'dynamic'
            elif prop['name'] == 'demo_prop_integer':
                prop['value'] = 7
            elif prop['name'] == 'demo_prop_boolean':
                prop['value'] = True
            elif prop['name'] == 'demo_prop_selection':
                prop['value'] = 'a'
        rec.write({'dynamic_properties': props})
        rec.invalidate_recordset(['dynamic_properties'])
        self.assertEqual(rec.dynamic_properties['demo_prop_char'], 'dynamic')
        self.assertEqual(rec.dynamic_properties['demo_prop_integer'], 7)
        self.assertTrue(rec.dynamic_properties['demo_prop_boolean'])
        self.assertEqual(rec.dynamic_properties['demo_prop_selection'], 'a')

    def test_field_convert_to_cache_selection_false(self):
        field = self.Showcase._fields['ref_model']
        rec = self.Showcase.new({'name': 'x', 'scalar_boolean_required': False})
        self.assertIsNone(field.convert_to_cache(False, rec))
