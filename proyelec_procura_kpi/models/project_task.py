from odoo import models, fields, api

PROP_OFERTADOS = 'd586b6ea5f215286'
PROP_GANADOS = '38a0d51c237f9082'
PROCURA_PROJECT_ID = 1019


class ProjectTask(models.Model):
    _inherit = 'project.task'

    x_kpi_efectividad = fields.Float(
        string='KPI Efectividad (%)',
        compute='_compute_kpi_efectividad',
        store=True,
        digits=(5, 2),
        group_operator='avg',
        help='(Renglones Ganados / Renglones Ofertados) * 100. Solo aplica al proyecto PROCURA.',
    )

    @api.depends('task_properties', 'project_id')
    def _compute_kpi_efectividad(self):
        for task in self:
            if task.project_id.id != PROCURA_PROJECT_ID:
                task.x_kpi_efectividad = 0.0
                continue

            props = task.task_properties
            if not props or not isinstance(props, dict):
                task.x_kpi_efectividad = 0.0
                continue

            ofertados = props.get(PROP_OFERTADOS, 0) or 0
            ganados = props.get(PROP_GANADOS, 0) or 0

            if ofertados > 0:
                task.x_kpi_efectividad = (ganados / ofertados) * 100
            else:
                task.x_kpi_efectividad = 0.0