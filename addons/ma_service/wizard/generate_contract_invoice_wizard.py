from odoo import api, fields, models, _
from odoo.exceptions import UserError


class GenerateContractInvoiceWizard(models.TransientModel):
    """
    Wizard to manually trigger invoice generation for a specific contract
    and billing month, bypassing the daily cron.
    """
    _name = 'ma.generate.contract.invoice.wizard'
    _description = 'Generate Contract Invoice'

    contract_id = fields.Many2one(
        'ma.service.contract',
        string='Contract',
        required=True,
    )
    invoice_date = fields.Date(
        string='Invoice Date',
        required=True,
        default=fields.Date.today,
    )
    monthly_fee = fields.Monetary(
        string='Amount',
        related='contract_id.monthly_fee',
        readonly=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='contract_id.currency_id',
    )

    def action_generate(self):
        self.ensure_one()
        if self.contract_id.state != 'active':
            raise UserError(_('Contract must be Active to generate an invoice.'))

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.contract_id.client_id.id,
            'invoice_date': self.invoice_date,
            'ref': self.contract_id.name,
            'narration': _('Monthly PRO contract fee — %s') % self.contract_id.name,
            'invoice_line_ids': [(0, 0, {
                'name': _('Monthly PRO Support Fee — %s') % self.contract_id.name,
                'quantity': 1,
                'price_unit': self.contract_id.monthly_fee,
            })],
        })
        self.contract_id.invoice_ids = [(4, invoice.id)]

        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoice Generated'),
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
        }
