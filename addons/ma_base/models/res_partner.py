from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    division_ids = fields.Many2many(
        'ma.division',
        'partner_division_rel',
        'partner_id',
        'division_id',
        string='Divisions',
    )
    client_type = fields.Selection([
        ('service', 'Service Client'),
        ('contracting', 'Contracting Client'),
        ('trading', 'Trading Client'),
        ('all', 'All Divisions'),
    ], string='Client Type', default='all')

    contracting_project_count = fields.Integer(
        string='Projects',
        compute='_compute_contracting_project_count',
    )
    service_job_count = fields.Integer(
        string='Service Jobs',
        compute='_compute_service_job_count',
    )

    def _compute_contracting_project_count(self):
        contracting_div = self.env['ma.division'].search([('code', '=', 'contracting')], limit=1)
        for partner in self:
            if contracting_div:
                partner.contracting_project_count = self.env['project.project'].search_count([
                    ('partner_id', 'in', [partner.id] + self.env['res.partner'].search([
                        ('commercial_partner_id', '=', partner.commercial_partner_id.id)
                    ]).ids),
                    ('division_id', '=', contracting_div.id),
                ])
            else:
                partner.contracting_project_count = 0

    def _compute_service_job_count(self):
        service_div = self.env['ma.division'].search([('code', '=', 'service')], limit=1)
        for partner in self:
            if service_div:
                partner.service_job_count = self.env['project.task'].search_count([
                    ('partner_id', '=', partner.id),
                    ('project_id.division_id', '=', service_div.id),
                ])
            else:
                partner.service_job_count = 0

    def action_view_contracting_projects(self):
        self.ensure_one()
        contracting_div = self.env['ma.division'].search([('code', '=', 'contracting')], limit=1)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Projects',
            'res_model': 'project.project',
            'view_mode': 'list,form,kanban',
            'domain': [
                ('partner_id', '=', self.id),
                ('division_id', '=', contracting_div.id if contracting_div else False),
            ],
            'context': {'default_partner_id': self.id},
        }

    def action_view_service_jobs(self):
        self.ensure_one()
        service_div = self.env['ma.division'].search([('code', '=', 'service')], limit=1)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service Jobs',
            'res_model': 'project.task',
            'view_mode': 'list,form,kanban',
            'domain': [
                ('partner_id', '=', self.id),
                ('project_id.division_id', '=', service_div.id if service_div else False),
            ],
            'context': {'default_partner_id': self.id},
        }
