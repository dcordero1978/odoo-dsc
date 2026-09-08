# -*- coding: utf-8 -*-
"""
Traduce al español las etiquetas de la ventana del Trial Balance (account.balance.report)
del kit, redefiniendo el string de los campos heredados. Aislado, no toca el módulo de terceros.
"""
from odoo import fields, models


class AccountBalanceReport(models.TransientModel):
    _inherit = "account.balance.report"

    # Título de la ventana
    name = fields.Char(default="Balanza de Comprobación")

    date_from = fields.Date(string="Fecha inicial")
    date_to = fields.Date(string="Fecha final")
    enable_filter = fields.Boolean(string="Habilitar comparación")

    # Opciones de radio traducidas al español
    target_move = fields.Selection(
        selection=[
            ("posted", "Asientos publicados"),
            ("all", "Todos los asientos"),
        ],
        string="Asientos",
        default="posted",
    )
    display_account = fields.Selection(
        selection=[
            ("all", "Todas las cuentas"),
            ("movement", "Con movimientos"),
            ("not_zero", "Con saldo distinto de cero"),
        ],
        string="Mostrar cuentas",
        default="movement",
    )
