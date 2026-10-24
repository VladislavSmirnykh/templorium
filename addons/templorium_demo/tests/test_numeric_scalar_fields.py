from decimal import Decimal

from odoo import fields
from odoo.orm.fields_numeric import _JS_MAX_SAFE_INTEGER
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install', 'templorium_demo')
class TestNumericScalarFields(TransactionCase):
    """big_integer / decimal ORM and web_read semantics (Templorium /web)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Showcase = cls.env['templorium.demo.showcase']
        cls._record = cls.Showcase.new({
            'name': 'Numeric probe',
            'scalar_boolean_required': False,
        })

    def _create_showcase(self, **extra):
        vals = {
            'name': 'Showcase record',
            'scalar_boolean_required': False,
            **extra,
        }
        return self.Showcase.create(vals)

    # --- BigInteger: convert_to_read (JS safe integer boundary) ---

    def test_big_integer_read_none(self):
        field = self.Showcase._fields['scalar_big_integer']
        self.assertIsNone(field.convert_to_read(None, self._record))

    def test_big_integer_read_within_js_safe_range_stays_int(self):
        field = self.Showcase._fields['scalar_big_integer']
        for value in (0, 42, -100, _JS_MAX_SAFE_INTEGER, -_JS_MAX_SAFE_INTEGER):
            with self.subTest(value=value):
                self.assertEqual(field.convert_to_read(value, self._record), value)
                self.assertIsInstance(field.convert_to_read(value, self._record), int)

    def test_big_integer_read_outside_js_safe_range_is_string(self):
        field = self.Showcase._fields['scalar_big_integer']
        cases = (
            _JS_MAX_SAFE_INTEGER + 1,
            -_JS_MAX_SAFE_INTEGER - 1,
            9223372036854775807,
            -9223372036854775808,
        )
        for value in cases:
            with self.subTest(value=value):
                read = field.convert_to_read(value, self._record)
                self.assertEqual(read, str(value))
                self.assertIsInstance(read, str)

    def test_big_integer_convert_to_cache_accepts_string(self):
        field = self.Showcase._fields['scalar_big_integer']
        self.assertEqual(
            field.convert_to_cache('9223372036854775807', self._record),
            9223372036854775807,
        )

    def test_big_integer_int64_max_min_db_roundtrip(self):
        for value in (9223372036854775807, -9223372036854775808):
            with self.subTest(value=value):
                rec = self._create_showcase(scalar_big_integer=value)
                rec.invalidate_recordset(['scalar_big_integer'])
                self.assertEqual(rec.scalar_big_integer, value)

    def test_big_integer_web_read_large_as_string(self):
        rec = self._create_showcase(scalar_big_integer=9223372036854775807)
        payload = rec.web_read({'scalar_big_integer': {}})[0]
        self.assertEqual(payload['scalar_big_integer'], '9223372036854775807')

    def test_big_integer_web_read_small_as_int(self):
        rec = self._create_showcase(scalar_big_integer=42)
        payload = rec.web_read({'scalar_big_integer': {}})[0]
        self.assertEqual(payload['scalar_big_integer'], 42)

    def test_big_integer_write_string_literal(self):
        rec = self._create_showcase()
        rec.write({'scalar_big_integer': '9223372036854775807'})
        self.assertEqual(rec.scalar_big_integer, 9223372036854775807)

    # --- Decimal: exact literals + string /web read ---

    def test_decimal_read_none(self):
        field = self.Showcase._fields['scalar_decimal']
        self.assertIsNone(field.convert_to_read(None, self._record))

    def test_decimal_literal_stored_exactly(self):
        field = self.Showcase._fields['scalar_decimal']
        self.assertEqual(
            field.convert_to_cache('2.2222222222222221', self._record),
            Decimal('2.2222222222222221'),
        )

    def test_decimal_read_returns_string(self):
        rec = self._create_showcase(scalar_decimal='2.2222222222222221')
        self.assertEqual(rec.read(['scalar_decimal'])[0]['scalar_decimal'], '2.2222222222222221')

    def test_decimal_web_read_string(self):
        rec = self._create_showcase(scalar_decimal='2.2222222222222221')
        payload = rec.web_read({'scalar_decimal': {}})[0]
        self.assertEqual(payload['scalar_decimal'], '2.2222222222222221')

    def test_decimal_db_roundtrip(self):
        rec = self._create_showcase(scalar_decimal='2.2222222222222221')
        rec.invalidate_recordset(['scalar_decimal'])
        self.assertEqual(
            rec.read(['scalar_decimal'])[0]['scalar_decimal'],
            '2.2222222222222221',
        )

    def test_decimal_convert_to_cache_from_string(self):
        field = self.Showcase._fields['scalar_decimal']
        self.assertEqual(field.convert_to_cache('1.5', self._record), Decimal('1.5'))

    def test_decimal_write_string_literal(self):
        rec = self._create_showcase()
        rec.write({'scalar_decimal': '2.2222222222222221'})
        self.assertEqual(rec.read(['scalar_decimal'])[0]['scalar_decimal'], '2.2222222222222221')

    def test_decimal_digits_rounding_on_field(self):
        field = fields.Decimal()
        field._digits = (16, 6)
        self.assertEqual(field.get_digits(self.env), (16, 6))
        self.assertEqual(field.convert_to_cache(1.23456789, self._record), Decimal('1.234568'))
        self.assertEqual(field.convert_to_read(Decimal('1.234568'), self._record), '1.234568')

    def test_decimal_column_type_is_numeric(self):
        field = self.Showcase._fields['scalar_decimal']
        self.assertEqual(field.column_type, ('numeric', 'numeric'))
        self.env.cr.execute(
            """
            SELECT udt_name FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
            """,
            (self.Showcase._table, 'scalar_decimal'),
        )
        self.assertEqual(self.env.cr.fetchone()[0], 'numeric')
