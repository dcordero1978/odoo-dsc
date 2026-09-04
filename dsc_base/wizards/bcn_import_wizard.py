# -*- coding: utf-8 -*-
from datetime import date

from odoo import api, fields, models


class BcnImportWizard(models.TransientModel):
    _name = "dsc.bcn.import.wizard"
    _description = "Importar tasas de cambio del BCN"

    anio = fields.Integer(string="Año", required=True, default=lambda s: date.today().year)
    mes = fields.Selection(
        selection=[
            ("1", "Enero"), ("2", "Febrero"), ("3", "Marzo"), ("4", "Abril"),
            ("5", "Mayo"), ("6", "Junio"), ("7", "Julio"), ("8", "Agosto"),
            ("9", "Septiembre"), ("10", "Octubre"), ("11", "Noviembre"), ("12", "Diciembre"),
        ],
        string="Mes", required=True,
        default=lambda s: str(date.today().month),
    )

    def action_importar(self):
        self.ensure_one()
        n = self.env["res.currency"].bcn_importar_mes(anio=self.anio, mes=int(self.mes))
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "BCN",
                "message": "%s tasas de cambio importadas para %s/%s." % (n, self.mes, self.anio),
                "type": "success",
                "sticky": False,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
