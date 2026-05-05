# -*- coding: utf-8 -*-
{
    'name': 'Proyelec - Salas de Reunión',
    'version': '17.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Privacidad, asistentes y agenda para reservaciones de sala',
    'author': 'Contables Boyer',
    'depends': ['room', 'mail', 'web_gantt'],
    'data': [
        'security/proyelec_salas_groups.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'views/room_booking_views.xml',
        'data/cron.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'proyelec_salas/static/src/room_booking_gantt_patch.js',
            'proyelec_salas/static/src/room_booking_calendar_patch.js',
        ],
    },
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
