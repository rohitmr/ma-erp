from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    job_sequence = fields.Char(
        string='Job No.',
        readonly=True,
        copy=False,
        index=True,
    )
    service_type_id = fields.Many2one(
        'ma.service.type',
        string='Service Type',
        index=True,
        tracking=True,
    )
    govt_reference = fields.Char(
        string='Government Reference',
        help='Transaction or reference number from the government authority.',
        tracking=True,
    )
    client_notes = fields.Text(
        string='Client Notes',
        help='Notes visible to the client on the portal.',
    )
    is_service_job = fields.Boolean(
        string='Is Service Job',
        compute='_compute_is_service_job',
        store=True,
    )
    is_overdue = fields.Boolean(
        string='Overdue',
        compute='_compute_is_overdue',
        store=True,
    )

    @api.depends('project_id.division_id.code')
    def _compute_is_service_job(self):
        for task in self:
            task.is_service_job = (
                task.project_id.division_id.code == 'service'
            )

    @api.depends('date_deadline', 'stage_id.is_closed')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for task in self:
            task.is_overdue = (
                bool(task.date_deadline)
                and task.date_deadline < today
                and not task.stage_id.is_closed
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('project_id'):
                project = self.env['project.project'].browse(vals['project_id'])
                if project.division_id and project.division_id.code == 'service':
                    if not vals.get('job_sequence'):
                        vals['job_sequence'] = self.env['ir.sequence'].next_by_code(
                            'ma.service.job'
                        ) or '/'
        return super().create(vals_list)
