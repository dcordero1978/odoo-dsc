# -*- coding: utf-8 -*-
"""
Agrega un diseño de cheque propio (en español) a la selección de
'Diseño del cheque'. Odoo Community trae account_check_printing pero SIN
ningún layout (solo 'disabled'); los layouts los aportan las localizaciones
(l10n_us_check_printing, etc.) que no vienen en este clone.

El valor de la selección debe ser el xmlID del ir.actions.report del cheque.
"""
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    account_check_printing_layout = fields.Selection(
        selection_add=[
            ("dsc_base.action_report_check_dsc", "Cheque estándar (DSC)"),
        ],
        ondelete={"dsc_base.action_report_check_dsc": "set default"},
    )
