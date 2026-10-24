from odoo import api, fields, models


class TemploriumDemoLine(models.Model):
    _name = 'templorium.demo.line'
    _description = 'Templorium Demo Line (One2many child)'
    _order = 'sequence, id'

    showcase_id = fields.Many2one(
        'templorium.demo.showcase',
        string='Parent showcase',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Line label', required=True)
    quantity = fields.Float(string='Quantity', digits=(16, 2))
    unit_price = fields.Monetary(string='Unit price', currency_field='currency_id')
    currency_id = fields.Many2one(
        related='showcase_id.currency_id',
        depends=['showcase_id'],
    )
    line_total = fields.Monetary(
        string='Line total (stored compute)',
        compute='_compute_line_total',
        store=True,
        currency_field='currency_id',
    )

    @api.depends('quantity', 'unit_price')
    def _compute_line_total(self):
        for line in self:
            line.line_total = (line.quantity or 0.0) * (line.unit_price or 0.0)
