from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    division_id = fields.Many2one(
        'ma.division',
        string='Division',
        index=True,
        tracking=True,
    )
