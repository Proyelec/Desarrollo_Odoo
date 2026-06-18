from odoo import models, fields


class ProyelecDepartamentoMedular(models.Model):
    _name = "proyelec.departamento.medular"
    _description = "Departamento Medular"
    _order = "name"

    name = fields.Char(string="Nombre", required=True)
    code = fields.Char(string="Código")
    active = fields.Boolean(string="Activo", default=True)

    _sql_constraints = [
        ("name_uniq", "UNIQUE(name)", "Ya existe un departamento con ese nombre."),
    ]
