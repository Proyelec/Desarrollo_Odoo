from . import models
from odoo import api, SUPERUSER_ID


def post_init_hook(env):
    grupo_user = env.ref('proyelec_salas.group_room_booking_user')
    grupo_leader = env.ref('proyelec_salas.group_room_booking_leader')

    usuarios_internos = env['res.users'].search([
        ('share', '=', False),
        ('active', '=', True),
    ])
    grupo_user.write({'users': [(4, u.id) for u in usuarios_internos]})

    LIDER_IDS = [115, 195, 126, 196, 166, 193, 199, 182, 200, 202, 118, 114]
    grupo_leader.write({'users': [(4, uid) for uid in LIDER_IDS]})
