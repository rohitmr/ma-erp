from odoo import fields, models


class MaProjectType(models.Model):
    _name = 'ma.project.type'
    _description = 'Contracting Project Type'
    _order = 'sequence, name'

    name = fields.Char(string='Project Type', required=True, translate=True)
    code = fields.Char(string='Code', size=20)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Project type code must be unique.'),
    ]
