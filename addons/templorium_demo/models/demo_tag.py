from random import randint

from odoo import fields, models


class TemploriumDemoTag(models.Model):
    _name = 'templorium.demo.tag'
    _description = 'Templorium Demo Tag (Many2many target)'
    _order = 'name'

    def _default_color(self):
        return randint(1, 11)

    name = fields.Char(string='Tag name', required=True)
    color = fields.Integer(string='Color index', default=lambda self: self._default_color())
