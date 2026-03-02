from odoo import api, fields, models


class MaDivision(models.Model):
    _name = 'ma.division'
    _description = 'Business Division'
    _order = 'sequence, name'

    name = fields.Char(string='Division Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True, size=20)
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index')
    description = fields.Text(string='Description', translate=True)

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Division code must be unique.'),
    ]

    @api.model
    def get_dashboard_data(self):
        """Aggregate KPI data for the unified dashboard."""
        AccountMove = self.env['account.move']
        ProjectTask = self.env['project.task']
        ProjectProject = self.env['project.project']
        HrEmployee = self.env['hr.employee']

        # --- Receivables ---
        receivable_data = AccountMove.read_group(
            domain=[
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial']),
            ],
            fields=['amount_residual:sum'],
            groupby=[],
        )
        total_receivables = receivable_data[0]['amount_residual'] if receivable_data else 0.0

        # --- Overdue invoices ---
        overdue_data = AccountMove.read_group(
            domain=[
                ('move_type', 'in', ['out_invoice', 'out_refund']),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial']),
                ('invoice_date_due', '<', fields.Date.today()),
            ],
            fields=['amount_residual:sum', 'id:count'],
            groupby=[],
        )
        overdue_amount = overdue_data[0]['amount_residual'] if overdue_data else 0.0
        overdue_count = overdue_data[0]['id_count'] if overdue_data else 0

        # --- Service: pending & overdue jobs ---
        service_division = self.search([('code', '=', 'service')], limit=1)
        pending_jobs = 0
        overdue_jobs = 0
        if service_division:
            pending_jobs = ProjectTask.search_count([
                ('project_id.division_id', '=', service_division.id),
                ('stage_id.fold', '=', False),
            ])
            overdue_jobs = ProjectTask.search_count([
                ('project_id.division_id', '=', service_division.id),
                ('stage_id.fold', '=', False),
                ('date_deadline', '<', fields.Date.today()),
            ])

        # --- Contracting: ongoing projects ---
        contracting_division = self.search([('code', '=', 'contracting')], limit=1)
        ongoing_projects = 0
        if contracting_division:
            ongoing_projects = ProjectProject.search_count([
                ('division_id', '=', contracting_division.id),
                ('last_update_status', 'not in', ['done', 'off_track']),
            ])

        # --- HR: documents expiring within 30 days ---
        expiring_docs = 0
        if 'ma.hr.document' in self.env:
            from datetime import date, timedelta
            today = date.today()
            in_30 = today + timedelta(days=30)
            expiring_docs = self.env['ma.hr.document'].search_count([
                ('expiry_date', '>=', fields.Date.to_string(today)),
                ('expiry_date', '<=', fields.Date.to_string(in_30)),
            ])

        currency = self.env.company.currency_id
        return {
            'total_receivables': total_receivables,
            'total_receivables_formatted': currency.symbol + ' ' + '{:,.2f}'.format(total_receivables),
            'overdue_amount': overdue_amount,
            'overdue_amount_formatted': currency.symbol + ' ' + '{:,.2f}'.format(overdue_amount),
            'overdue_count': overdue_count,
            'pending_jobs': pending_jobs,
            'overdue_jobs': overdue_jobs,
            'ongoing_projects': ongoing_projects,
            'expiring_docs': expiring_docs,
            'currency_symbol': currency.symbol,
        }
