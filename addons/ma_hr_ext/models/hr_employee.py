from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # --- Passport ---
    passport_no = fields.Char(string='Passport No.', groups='hr.group_hr_user')
    passport_expiry = fields.Date(string='Passport Expiry', groups='hr.group_hr_user')

    # --- National ID (generic: Emirates ID / QID / Iqama / etc.) ---
    national_id_no = fields.Char(string='National ID No.', groups='hr.group_hr_user')
    national_id_expiry = fields.Date(
        string='National ID Expiry', groups='hr.group_hr_user'
    )

    # --- Visa ---
    visa_no = fields.Char(string='Visa No.', groups='hr.group_hr_user')
    visa_type = fields.Selection([
        ('employment', 'Employment Visa'),
        ('residence', 'Residence Visa'),
        ('visit', 'Visit Visa'),
        ('other', 'Other'),
    ], string='Visa Type', groups='hr.group_hr_user')
    visa_expiry = fields.Date(string='Visa Expiry', groups='hr.group_hr_user')

    # --- Labour Card ---
    labour_card_no = fields.Char(string='Labour Card No.', groups='hr.group_hr_user')
    labour_card_expiry = fields.Date(
        string='Labour Card Expiry', groups='hr.group_hr_user'
    )

    # --- Health Card ---
    health_card_no = fields.Char(string='Health Card No.', groups='hr.group_hr_user')
    health_card_expiry = fields.Date(
        string='Health Card Expiry', groups='hr.group_hr_user'
    )

    # --- Documents (generic model) ---
    document_ids = fields.One2many(
        'ma.hr.document',
        'employee_id',
        string='Documents',
    )
    document_count = fields.Integer(
        string='Documents',
        compute='_compute_document_count',
    )
    expiring_document_count = fields.Integer(
        string='Expiring Documents',
        compute='_compute_document_count',
    )

    @api.depends('document_ids', 'document_ids.expiry_status')
    def _compute_document_count(self):
        for emp in self:
            emp.document_count = len(emp.document_ids)
            emp.expiring_document_count = len(
                emp.document_ids.filtered(
                    lambda d: d.expiry_status in ('expiring_soon', 'expired')
                )
            )
