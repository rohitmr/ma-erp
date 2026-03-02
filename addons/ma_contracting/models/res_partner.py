from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Summary figures computed across all contracting projects for this partner
    contracting_total_value = fields.Monetary(
        string='Total Project Value',
        compute='_compute_contracting_summary',
        currency_field='currency_id',
    )
    contracting_total_invoiced = fields.Monetary(
        string='Total Invoiced',
        compute='_compute_contracting_summary',
        currency_field='currency_id',
    )
    contracting_total_received = fields.Monetary(
        string='Total Received',
        compute='_compute_contracting_summary',
        currency_field='currency_id',
    )
    contracting_pending_balance = fields.Monetary(
        string='Pending Balance',
        compute='_compute_contracting_summary',
        currency_field='currency_id',
    )
    contracting_max_overdue_days = fields.Integer(
        string='Max Overdue Days',
        compute='_compute_contracting_summary',
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )

    def _compute_contracting_summary(self):
        contracting_div = self.env['ma.division'].search(
            [('code', '=', 'contracting')], limit=1
        )
        for partner in self:
            projects = self.env['project.project'].search([
                ('partner_id', '=', partner.id),
                ('division_id', '=', contracting_div.id if contracting_div else False),
            ])
            partner.contracting_total_value = sum(projects.mapped('contract_value'))
            partner.contracting_total_invoiced = sum(projects.mapped('total_invoiced'))
            partner.contracting_total_received = sum(projects.mapped('total_received'))
            partner.contracting_pending_balance = sum(
                projects.mapped('pending_balance')
            )
            partner.contracting_max_overdue_days = max(
                projects.mapped('overdue_days') or [0]
            )
