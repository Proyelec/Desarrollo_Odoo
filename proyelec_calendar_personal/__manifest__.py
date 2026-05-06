# -*- coding: utf-8 -*-
{
    'name': 'Proyelec - Calendario Personal',
    'version': '17.0.1.0.0',
    'summary': 'Calendario personal por usuario con sincronización de salas',
    'author': 'AIT - Proyelec',
    'category': 'Productivity',
    'depends': [
        'calendar',
        'proyelec_salas',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/calendar_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}