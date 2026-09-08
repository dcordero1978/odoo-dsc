# -*- coding: utf-8 -*-
{
    'name': 'DSC Base',
    'version': '19.0.1.0.0',
    'summary': 'Módulo base de personalizaciones DSC para Odoo 19',
    'description': """
DSC Base
========
Módulo base para las personalizaciones de DSC / ECSESA sobre Odoo 19 Community.
Sirve como punto de partida para modelos, vistas y lógica de negocio propias.
""",
    'author': 'DSC - dcordero1978',
    'website': 'https://github.com/dcordero1978/odoo-dsc',
    'category': 'Customizations',
    'license': 'LGPL-3',
    # account y base_accounting_kit: referenciamos sus menús para reorganizarlos
    'depends': ['base', 'account', 'base_accounting_kit'],
    'data': [
        'security/ir.model.access.csv',
        'views/dsc_base_views.xml',
        'views/accounting_menus.xml',
        'data/bcn_cron.xml',
        'wizards/bcn_import_wizard_views.xml',
        'wizards/trial_balance_wizard_views.xml',
        'views/account_move_bcn_views.xml',
        'report/report_trial_balance_dsc_template.xml',
    ],
    'external_dependencies': {'python': ['lxml', 'requests']},
    'installable': True,
    'application': False,
    'auto_install': False,
}
