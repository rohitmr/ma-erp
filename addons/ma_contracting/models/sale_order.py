from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    client_po_number = fields.Char(
        string='Client PO No.',
        tracking=True,
        help='Purchase Order number received from the client.',
    )
    client_npo_number = fields.Char(
        string='Client NPO No.',
        tracking=True,
        help='Notification of Purchase Order (NPO) number.',
    )
    project_type_id = fields.Many2one(
        'ma.project.type',
        string='Project Type',
        tracking=True,
    )
