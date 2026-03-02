from datetime import date, timedelta
from odoo import api, fields, models


class MaHrDocument(models.Model):
    _name = 'ma.hr.document'
    _description = 'Employee Document'
    _order = 'expiry_date asc, employee_id'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        ondelete='cascade',
        index=True,
    )
    document_type_id = fields.Many2one(
        'ma.hr.document.type',
        string='Document Type',
        required=True,
    )
    document_no = fields.Char(string='Document Number')
    issue_date = fields.Date(string='Issue Date')
    expiry_date = fields.Date(string='Expiry Date')
    file = fields.Binary(string='Scan / File', attachment=True)
    file_name = fields.Char(string='File Name')
    notes = fields.Text(string='Notes')

    expiry_status = fields.Selection([
        ('valid', 'Valid'),
        ('expiring_soon', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('no_expiry', 'No Expiry'),
    ], string='Expiry Status', compute='_compute_expiry_status', store=True)

    days_to_expiry = fields.Integer(
        string='Days to Expiry',
        compute='_compute_expiry_status',
        store=True,
    )

    @api.depends('expiry_date', 'document_type_id.has_expiry')
    def _compute_expiry_status(self):
        today = date.today()
        for rec in self:
            if not rec.document_type_id.has_expiry or not rec.expiry_date:
                rec.expiry_status = 'no_expiry'
                rec.days_to_expiry = 0
                continue
            delta = (rec.expiry_date - today).days
            rec.days_to_expiry = delta
            if delta < 0:
                rec.expiry_status = 'expired'
            elif delta <= 30:
                rec.expiry_status = 'expiring_soon'
            else:
                rec.expiry_status = 'valid'

    @api.model
    def _check_expiring_documents(self):
        """
        Daily cron: Send expiry alerts at 60, 30, 15, and 7 days before expiry.
        """
        today = date.today()
        thresholds = [60, 30, 15, 7]
        template = self.env.ref(
            'ma_hr_ext.email_template_document_expiry', raise_if_not_found=False
        )
        for days in thresholds:
            target_date = today + timedelta(days=days)
            expiring = self.search([
                ('expiry_date', '=', fields.Date.to_string(target_date)),
                ('document_type_id.has_expiry', '=', True),
            ])
            for doc in expiring:
                if template:
                    template.with_context(days_remaining=days).send_mail(
                        doc.id, force_send=False
                    )
                # Also create an activity on the employee record
                doc.employee_id.activity_schedule(
                    'mail.mail_activity_data_todo',
                    date_deadline=doc.expiry_date,
                    summary='Document Expiring: %s' % doc.document_type_id.name,
                    note='%s — %s expires in %d days on %s.' % (
                        doc.employee_id.name,
                        doc.document_type_id.name,
                        days,
                        doc.expiry_date,
                    ),
                    user_id=doc.employee_id.parent_id.user_id.id
                    or self.env.ref('base.user_admin').id,
                )
