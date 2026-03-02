from odoo import api, fields, models, _


class MaProjectPayment(models.Model):
    _name = 'ma.project.payment'
    _description = 'Project Payment Milestone'
    _order = 'sequence, id'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Milestone', required=True)
    payment_type = fields.Selection([
        ('advance', 'Advance'),
        ('progress', 'Progress Billing'),
        ('retention', 'Retention Release'),
        ('final', 'Final Payment'),
        ('other', 'Other'),
    ], string='Type', required=True, default='progress')

    percentage = fields.Float(
        string='% of Contract',
        digits=(5, 2),
        help='Percentage of the contract value. Fills Amount automatically.',
    )
    amount = fields.Monetary(
        string='Amount',
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='project_id.currency_id',
        store=True,
    )
    due_date = fields.Date(string='Due Date')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('invoiced', 'Invoiced'),
        ('received', 'Received'),
        ('overdue', 'Overdue'),
    ], string='Status', default='pending', compute='_compute_state', store=True)

    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice',
        copy=False,
    )
    payment_date = fields.Date(string='Payment Date', readonly=True)
    notes = fields.Text(string='Notes')

    @api.depends('invoice_id', 'invoice_id.payment_state', 'due_date')
    def _compute_state(self):
        today = fields.Date.today()
        for rec in self:
            if rec.invoice_id:
                if rec.invoice_id.payment_state in ('paid', 'in_payment'):
                    rec.state = 'received'
                    if not rec.payment_date:
                        rec.payment_date = today
                else:
                    if rec.due_date and rec.due_date < today:
                        rec.state = 'overdue'
                    else:
                        rec.state = 'invoiced'
            else:
                if rec.due_date and rec.due_date < today and rec.payment_type != 'retention':
                    rec.state = 'overdue'
                else:
                    rec.state = 'pending'

    @api.onchange('percentage', 'project_id')
    def _onchange_percentage(self):
        if self.percentage and self.project_id and self.project_id.contract_value:
            self.amount = self.project_id.contract_value * self.percentage / 100

    def action_create_invoice(self):
        self.ensure_one()
        if self.invoice_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'res_id': self.invoice_id.id,
                'view_mode': 'form',
            }
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.project_id.partner_id.id,
            'invoice_date': fields.Date.today(),
            'division_id': self.project_id.division_id.id,
            'ref': self.project_id.name,
            'invoice_line_ids': [(0, 0, {
                'name': _('%s — %s') % (self.project_id.name, self.name),
                'quantity': 1,
                'price_unit': self.amount,
            })],
        })
        self.invoice_id = invoice
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
        }
