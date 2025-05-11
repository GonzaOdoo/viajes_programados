# -*- coding: utf-8 -*-
{
    'name': "Viajes Programados",

    'summary': """
        Módulo para gestionar viajes programados""",

    'description': """
        Este módulo permite gestionar viajes programados en Odoo.
    """,

    'author': "GonzaOdoo",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['fleet','sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/viajes_views.xml',
        'views/sale_order.xml',
        'views/fleet_vehicle_views.xml',
        'data/secuencia_viajes.xml',
    ],
    'license':'LGPL-3',
}
