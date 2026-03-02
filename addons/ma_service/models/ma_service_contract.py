from datetime import date, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MaServiceContract(models.Model):
    _name = 'ma.service.contract'
    _description = 'PRO Service Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    name = fields.Char(
        string='Contract No.',
        readonly=True,
        copy=False,
        default='/',
        index=True,
    )
    client_id = fields.Many2one(
        'res.partner',
        string='Client',
        required=True,
        tracking=True,
        domain=[('is_company', '=', True)],
    )
    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    monthly_fee = fields.Monetary(
        string='Monthly Fee',
        required=True,
        currency_field='currency_id',
        tracking=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
    )
    billing_day = fields.Integer(
        string='Billing Day',
        default=1,
        help='Day of the month on which the recurring invoice is generated (1–28).',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    line_ids = fields.One2many(
        'ma.service.contract.line',
        'contract_id',
        string='Services Included',
    )
    invoice_ids = fields.Many2many(
        'account.move',
        'service_contract_invoice_rel',
        'contract_id',
        'invoice_id',
        string='Invoices',
        copy=False,
    )
    invoice_count = fields.Integer(
        string='Invoice Count',
        compute='_compute_invoice_count',
    )
    note = fields.Text(string='Internal Notes')
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )

    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for contract in self:
            contract.invoice_count = len(contract.invoice_ids)

    @api.constrains('billing_day')
    def _check_billing_day(self):
        for rec in self:
            if not 1 <= rec.billing_day <= 28:
                raise UserError(_('Billing Day must be between 1 and 28.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'ma.service.contract'
                ) or '/'
        return super().create(vals_list)

    def action_activate(self):
        for rec in self:
            rec.state = 'active'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'

    def action_view_invoices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoices'),
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.invoice_ids.ids)],
        }

    def _generate_monthly_invoice(self):
        """Called by cron: create a draft invoice for contracts billing today."""
        today = date.today()
        contracts = self.search([
            ('state', '=', 'active'),
            ('billing_day', '=', today.day),
        ])
        for contract in contracts:
            if contract.end_date and contract.end_date < today:
                contract.state = 'expired'
                continue
            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'partner_id': contract.client_id.id,
                'invoice_date': today,
                'division_id': self.env['ma.division'].search(
                    [('code', '=', 'service')], limit=1
                ).id,
                'ref': contract.name,
                'narration': _('Monthly PRO contract fee — %s') % contract.name,
                'invoice_line_ids': [(0, 0, {
                    'name': _('Monthly PRO Support Fee — %s') % contract.name,
                    'quantity': 1,
                    'price_unit': contract.monthly_fee,
                })],
            })
            contract.invoice_ids = [(4, invoice.id)]
            template = self.env.ref(
                'ma_service.email_template_contract_invoice', raise_if_not_found=False
            )
            if template:
                template.send_mail(invoice.id, force_send=False)

    def _check_expiring_contracts(self):
        """Called by cron: alert on contracts expiring within 30 days."""
        today = date.today()
        warning_date = today + timedelta(days=30)
        expiring = self.search([
            ('state', '=', 'active'),
            ('end_date', '>=', fields.Date.to_string(today)),
            ('end_date', '<=', fields.Date.to_string(warning_date)),
        ])
        for contract in expiring:
            contract.activity_schedule(
                'mail.mail_activity_data_todo',
                date_deadline=contract.end_date,
                summary=_('Contract Expiring Soon: %s') % contract.name,
                note=_('Contract %s with %s expires on %s.') % (
                    contract.name,
                    contract.client_id.name,
                    contract.end_date,
                ),
            )


class MaServiceContractLine(models.Model):
    _name = 'ma.service.contract.line'
    _description = 'PRO Contract Service Line'
    _order = 'sequence'

    contract_id = fields.Many2one(
        'ma.service.contract',
        string='Contract',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(default=10)
    service_type_id = fields.Many2one(
        'ma.service.type',
        string='Service Type',
        required=True,
    )
    description = fields.Char(string='Description')
    quantity_per_month = fields.Integer(string='Units / Month', default=1)
