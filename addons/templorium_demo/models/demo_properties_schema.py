from odoo import fields, models


class TemploriumDemoPropertiesSchema(models.Model):
    _name = 'templorium.demo.properties.schema'
    _description = 'Templorium Demo Properties Schema'
    _order = 'name'

    name = fields.Char(string='Schema name', required=True)
    properties_definition = fields.PropertiesDefinition(string='Properties definition')
