from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    division_id = fields.Many2one(
        'ma.division',
        string='Division',
        index=True,
        tracking=True,
    )
