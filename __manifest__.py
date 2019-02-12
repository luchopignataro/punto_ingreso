# -*- coding: utf-8 -*-
{
    'name': "Punto Ingreso",

    'summary': """Manage services, patients, doctors and places""",

    'description': """
        Punto ingreso module for managing:
            - services
            - patients
            - doctors
            - places
            - etc.
    """,

    'author': "PersiscalConsulting LLC.",
    'website': "https://persiscalconsulting.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.20',

    # any module necessary for this one to work correctly
    'depends': ['base','product', 'crm', 'account'],

    # always loaded
    'data': [
        'views/estudios.xml',
        'views/subservicios.xml',
        'views/partner.xml',
        'views/odoo_studio.xml',
        'views/estudio_estados.xml',
        'views/paciente_estados.xml',
        'views/precio_honor.xml',
        'views/multiplicadores_product_template.xml',
        'views/crm_lead_form_carga.xml',
        'views/facturacion.xml',
        'reports/paciente_report.xml',
        'reports/estudios_report.xml',
        'security/puntoingreso_security.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo.xml',
    # ],

    'application' : True,

    'images': ['static/description/icon.png'],
}
