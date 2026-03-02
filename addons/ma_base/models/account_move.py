from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    division_id = fields.Many2one(
        'ma.division',
        string='Division',
        index=True,
        tracking=True,
    )
