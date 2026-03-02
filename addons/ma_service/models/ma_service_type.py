from odoo import fields, models


class MaServiceType(models.Model):
    _name = 'ma.service.type'
    _description = 'Service Type'
    _order = 'sequence, name'

    name = fields.Char(string='Service Type', required=True, translate=True)
    code = fields.Char(string='Code', size=20)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    default_fee = fields.Monetary(
        string='Default Fee',
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    description = fields.Text(string='Description', translate=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Service type code must be unique.'),
    ]
