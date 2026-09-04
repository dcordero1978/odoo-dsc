# -*- coding: utf-8 -*-
from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_bcn_traer_tasa(self):
        """Trae del BCN la tasa del día de la factura (o de hoy) y la registra.

        Útil cuando el cron está apagado o aún no existe la tasa de esa fecha.
        Tras registrarla, Odoo recalcula invoice_currency_rate al recargar.
        """
        self.ensure_one()
        fecha = self.invoice_date or self.date
        rate = self.env["res.currency"].bcn_importar_dia(fecha=fecha)
        if not rate:
            raise UserError(_("No se pudo obtener la tasa del BCN para %s.") % fecha)
        # forzar recálculo del tipo de cambio del documento
        self.invalidate_recordset(["invoice_currency_rate"])
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "BCN",
                "message": _("Tasa del %s actualizada: %.4f NIO por USD.") % (
                    fecha, (1.0 / rate) if rate else 0.0),
                "type": "success",
                "sticky": False,
            },
        }
