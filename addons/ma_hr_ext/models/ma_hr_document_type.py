from odoo import fields, models


class MaHrDocumentType(models.Model):
    _name = 'ma.hr.document.type'
    _description = 'Employee Document Type'
    _order = 'sequence, name'

    name = fields.Char(string='Document Type', required=True, translate=True)
    code = fields.Char(string='Code', size=20)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    has_expiry = fields.Boolean(
        string='Has Expiry Date',
        default=True,
        help='Uncheck for documents that do not expire (e.g. certificates).',
    )

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Document type code must be unique.'),
    ]
