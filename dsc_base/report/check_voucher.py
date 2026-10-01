# -*- coding: utf-8 -*-
"""
Comprobante de Cheque (voucher) tamaño carta: cheque arriba + asiento contable abajo.
Estilo contabilidad nicaragüense (ContSis). Es un reporte NUEVO, no modifica el
formato de cheque nativo. Botón aparte en el pago.
"""
from odoo import _, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _comprobante_cheque_lineas(self):
        """Devuelve las líneas del asiento contable para el comprobante."""
        self.ensure_one()
        lineas = []
        for aml in self.move_id.line_ids.sorted(lambda l: (l.credit, l.id)):
            lineas.append({
                "cuenta": aml.account_id.code,
                "cuenta_nombre": aml.account_id.name,
                "descripcion": aml.name or "",
                "centro": ", ".join(
                    aml.analytic_distribution and [
                        self.env["account.analytic.account"].browse(int(k)).name
                        for k in aml.analytic_distribution.keys()
                    ] or []
                ),
                "debito": aml.debit,
                "credito": aml.credit,
            })
        return lineas

    def action_imprimir_comprobante_cheque(self):
        self.ensure_one()
        return self.env.ref(
            "dsc_base.action_report_check_voucher_dsc"
        ).report_action(self)
