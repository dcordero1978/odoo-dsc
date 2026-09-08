# -*- coding: utf-8 -*-
"""
Traduce al español las etiquetas de la ventana del Trial Balance (account.balance.report)
del kit, redefiniendo el string de los campos heredados. Aislado, no toca el módulo de terceros.
"""
from odoo import fields, models


class AccountBalanceReport(models.TransientModel):
    _inherit = "account.balance.report"

    date_from = fields.Date(string="Fecha inicial")
    date_to = fields.Date(string="Fecha final")
    target_move = fields.Selection(string="Asientos")
    display_account = fields.Selection(string="Mostrar cuentas")
    enable_filter = fields.Boolean(string="Habilitar comparación")
