from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    homologado_db_url = fields.Char(
        string="URL Odoo Homologado",
        config_parameter="homologado.db.url"
    )
    homologado_db_name = fields.Char(
        string="Nombre BD Homologada",
        config_parameter="homologado.db.name"
    )
    homologado_db_user = fields.Char(
        string="Usuario API Homologado",
        config_parameter="homologado.db.user"
    )
    homologado_db_password = fields.Char(
        string="Password API Homologado",
        config_parameter="homologado.db.password"
    )
