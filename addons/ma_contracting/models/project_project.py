from odoo import api, fields, models, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_type_id = fields.Many2one(
        'ma.project.type',
        string='Project Type',
        tracking=True,
    )
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
    contract_value = fields.Monetary(
        string='Contract Value',
        currency_field='currency_id',
        tracking=True,
        help='Total agreed contract value.',
    )
    retention_percentage = fields.Float(
        string='Retention %',
        digits=(5, 2),
        default=0.0,
        tracking=True,
        help='Percentage withheld by client until project completion.',
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )

    payment_ids = fields.One2many(
        'ma.project.payment',
        'project_id',
        string='Payment Milestones',
    )
    payment_count = fields.Integer(
        compute='_compute_payment_count',
        string='Milestones',
    )

    # --- Financial computed fields ---
    total_invoiced = fields.Monetary(
        string='Total Invoiced',
        compute='_compute_financials',
        store=True,
        currency_field='currency_id',
    )
    total_received = fields.Monetary(
        string='Total Received',
        compute='_compute_financials',
        store=True,
        currency_field='currency_id',
    )
    pending_balance = fields.Monetary(
        string='Pending Balance',
        compute='_compute_financials',
        store=True,
        currency_field='currency_id',
    )
    retention_amount = fields.Monetary(
        string='Retention Amount',
        compute='_compute_retention_amount',
        currency_field='currency_id',
    )
    profitability_amount = fields.Monetary(
        string='Gross Profit',
        compute='_compute_profitability',
        currency_field='currency_id',
    )
    profitability_percentage = fields.Float(
        string='Profit %',
        compute='_compute_profitability',
        digits=(5, 2),
    )
    overdue_days = fields.Integer(
        string='Overdue Days',
        compute='_compute_overdue_days',
    )

    def _compute_payment_count(self):
        for proj in self:
            proj.payment_count = len(proj.payment_ids)

    @api.depends('payment_ids.invoice_id', 'payment_ids.invoice_id.payment_state',
                 'payment_ids.amount')
    def _compute_financials(self):
        for proj in self:
            invoiced = 0.0
            received = 0.0
            for milestone in proj.payment_ids:
                if milestone.invoice_id and milestone.invoice_id.state == 'posted':
                    invoiced += milestone.amount
                    if milestone.invoice_id.payment_state in ('paid', 'in_payment'):
                        received += milestone.amount
            proj.total_invoiced = invoiced
            proj.total_received = received
            proj.pending_balance = invoiced - received

    @api.depends('contract_value', 'retention_percentage')
    def _compute_retention_amount(self):
        for proj in self:
            proj.retention_amount = proj.contract_value * proj.retention_percentage / 100

    def _compute_profitability(self):
        AccountMove = self.env['account.move']
        for proj in self:
            # Sum of vendor bills (costs) linked to this project via analytic account
            costs = 0.0
            if proj.analytic_account_id:
                bills = AccountMove.search([
                    ('move_type', 'in', ['in_invoice', 'in_refund']),
                    ('state', '=', 'posted'),
                    ('line_ids.analytic_distribution', 'like',
                     str(proj.analytic_account_id.id)),
                ])
                costs = sum(bills.mapped('amount_untaxed'))
            proj.profitability_amount = proj.contract_value - costs
            proj.profitability_percentage = (
                (proj.profitability_amount / proj.contract_value * 100)
                if proj.contract_value else 0.0
            )

    def _compute_overdue_days(self):
        today = fields.Date.today()
        for proj in self:
            overdue = 0
            for milestone in proj.payment_ids:
                if (milestone.state in ('invoiced', 'overdue')
                        and milestone.due_date
                        and milestone.due_date < today):
                    days = (today - milestone.due_date).days
                    overdue = max(overdue, days)
            proj.overdue_days = overdue

    def action_view_payment_milestones(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Payment Milestones'),
            'res_model': 'ma.project.payment',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def _create_retention_milestone(self):
        """Auto-create a retention milestone when retention % is set."""
        for proj in self:
            if proj.retention_percentage and proj.contract_value:
                existing = proj.payment_ids.filtered(
                    lambda p: p.payment_type == 'retention'
                )
                if not existing:
                    self.env['ma.project.payment'].create({
                        'project_id': proj.id,
                        'name': _('Retention Release'),
                        'payment_type': 'retention',
                        'percentage': proj.retention_percentage,
                        'amount': proj.contract_value * proj.retention_percentage / 100,
                        'sequence': 999,
                        'notes': _('Auto-created from retention % setting.'),
                    })

    def write(self, vals):
        res = super().write(vals)
        if 'retention_percentage' in vals or 'contract_value' in vals:
            self._create_retention_milestone()
        return res
