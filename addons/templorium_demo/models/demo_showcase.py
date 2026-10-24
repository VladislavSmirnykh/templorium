from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class TemploriumDemoShowcase(models.Model):
    _name = 'templorium.demo.showcase'
    _description = 'Templorium Demo Showcase'
    _order = 'name'

    name = fields.Char(string='Title (required Char)', required=True)
    active = fields.Boolean(string='Active', default=True)
    notes = fields.Text(string='Notes (optional Text)')

    # --- Scalars (NULL vs zero vs false) ---
    scalar_char_optional = fields.Char(string='Char optional (empty → NULL)')
    scalar_html = fields.Html(string='Html (html_editor widget)')
    scalar_integer = fields.Integer(string='Integer (NULL if unset)')
    scalar_big_integer = fields.BigInteger(
        string='Big integer (int8, ±9.22×10¹⁸)',
    )
    scalar_float = fields.Float(string='Float (float8 / numeric, no digit cap in demo)')
    scalar_decimal = fields.Decimal(string='Decimal (exact literal, numeric in DB)')
    scalar_monetary = fields.Monetary(string='Monetary', currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency (for Monetary)',
        default=lambda self: self.env.company.currency_id,
    )
    scalar_boolean_required = fields.Boolean(string='Boolean required', required=True, default=False)
    scalar_boolean_nullable = fields.Boolean(string='Boolean nullable (indeterminate when NULL)')
    scalar_selection = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
        ],
        string='Selection (NULL if unset)',
    )
    scalar_date = fields.Date(string='Date')
    scalar_datetime = fields.Datetime(string='Datetime')
    scalar_binary = fields.Binary(string='Binary file', attachment=True)
    scalar_binary_filename = fields.Char(string='Binary filename')
    scalar_image = fields.Image(string='Image', max_width=1024, max_height=1024)
    scalar_json = fields.Json(string='Json (raw JSON column)')

    kanban_stage = fields.Selection(
        selection=[
            ('new', 'New'),
            ('progress', 'In progress'),
            ('done', 'Done'),
        ],
        string='Kanban stage',
        default='new',
        required=True,
    )

    # --- Relational ---
    rel_partner_id = fields.Many2one('res.partner', string='Many2one → res.partner')
    rel_tag_ids = fields.Many2many(
        'templorium.demo.tag',
        'templorium_demo_showcase_tag_rel',
        'showcase_id',
        'tag_id',
        string='Many2many tags',
    )
    rel_line_ids = fields.One2many(
        'templorium.demo.line',
        'showcase_id',
        string='One2many lines',
    )

    ref_model = fields.Selection(
        selection=[
            ('templorium.demo.ref.target', 'Demo ref target'),
            ('res.partner', 'Partner'),
        ],
        string='Reference model name',
    )
    ref_id = fields.Many2oneReference(
        string='Many2oneReference / dynamic model',
        model_field='ref_model',
    )
    ref_classic = fields.Reference(
        selection=[
            ('templorium.demo.ref.target', 'Demo ref target'),
            ('res.partner', 'Partner'),
        ],
        string='Reference (classic Reference field)',
    )

    properties_schema_id = fields.Many2one(
        'templorium.demo.properties.schema',
        string='Properties schema',
        default=lambda self: self.env.ref(
            'templorium_demo.demo_properties_schema_default',
            raise_if_not_found=False,
        ),
    )
    dynamic_properties = fields.Properties(
        string='Properties (schema-driven)',
        definition='properties_schema_id.properties_definition',
        copy=True,
    )

    # --- Related ---
    related_partner_email = fields.Char(
        string='Related: partner email',
        related='rel_partner_id.email',
        readonly=False,
    )

    # --- Compute (stored) ---
    compute_operand_a = fields.Integer(string='Compute operand A')
    compute_operand_b = fields.Integer(string='Compute operand B')
    compute_sum_stored = fields.Integer(
        string='Stored compute: A + B',
        compute='_compute_sum_stored',
        store=True,
    )

    # --- Compute (non-stored) ---
    compute_label_preview = fields.Char(
        string='Non-stored compute: title preview',
        compute='_compute_label_preview',
    )

    # --- Onchange (client-side until save) ---
    onchange_quantity = fields.Float(string='Onchange quantity')
    onchange_unit_price = fields.Float(string='Onchange unit price')
    onchange_hint = fields.Char(string='Onchange hint (set in browser)')

    # --- Constraint demo ---
    constraint_min_name_len = fields.Integer(
        string='Min name length (SQL/Python constraint)',
        default=3,
        help='Title must be at least this many characters.',
    )

    @api.depends('compute_operand_a', 'compute_operand_b')
    def _compute_sum_stored(self):
        for record in self:
            record.compute_sum_stored = (record.compute_operand_a or 0) + (record.compute_operand_b or 0)

    @api.depends('name')
    def _compute_label_preview(self):
        for record in self:
            record.compute_label_preview = _('Preview: %s') % (record.name or '—')

    @api.onchange('onchange_quantity', 'onchange_unit_price')
    def _onchange_quantity_price(self):
        qty = self.onchange_quantity or 0.0
        price = self.onchange_unit_price or 0.0
        self.onchange_hint = _('Onchange: %(qty)s × %(price)s = %(total)s (not saved until you click Save)') % {
            'qty': qty,
            'price': price,
            'total': qty * price,
        }

    def action_kanban_stage_new(self):
        self.write({'kanban_stage': 'new'})

    def action_kanban_stage_progress(self):
        self.write({'kanban_stage': 'progress'})

    def action_kanban_stage_done(self):
        self.write({'kanban_stage': 'done'})

    def action_send_bus_notification(self):
        self.ensure_one()
        message = _(
            'Ping via bus.bus for “%(name)s” (record %(id)s).',
        ) % {'name': self.name, 'id': self.id}
        self.env.user._bus_send(
            'simple_notification',
            {
                'title': _('Bus bus'),
                'message': message,
                'type': 'success',
                'sticky': False,
            },
        )
        return True

    @api.constrains('name', 'constraint_min_name_len')
    def _check_name_min_length(self):
        for record in self:
            minimum = record.constraint_min_name_len or 0
            if minimum and record.name and len(record.name) < minimum:
                raise ValidationError(
                    _('Title must be at least %(min)s characters (Python @api.constrains).') % {'min': minimum}
                )
