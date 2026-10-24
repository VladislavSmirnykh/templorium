from odoo import fields, models


class TemploriumDemoRefTarget(models.Model):
    _name = 'templorium.demo.ref.target'
    _description = 'Templorium Demo Reference Target'
    _order = 'name'

    name = fields.Char(string='Target label', required=True)
    note = fields.Text(string='Note')
