# -*- coding: utf-8 -*-
"""
Extiende el reporte Trial Balance de base_accounting_kit para agregar el
Saldo Inicial (balance acumulado ANTES de date_from) por cuenta.

No modifica el módulo de terceros: hereda su AbstractModel y sobrescribe
_get_accounts para inyectar 'saldo_inicial' en cada fila. El débito/crédito/
saldo del período los sigue calculando la lógica original del kit.
"""
from odoo import models


class ReportTrialBalanceDsc(models.AbstractModel):
    _inherit = "report.base_accounting_kit.report_trial_balance"

    def _get_accounts(self, accounts, display_account):
        # Datos del período (débito, crédito, balance) tal como los calcula el kit
        account_res = super()._get_accounts(accounts, display_account)

        # Fecha de corte para el saldo inicial: lo que haya en used_context['date_from']
        ctx = self.env.context or {}
        date_from = ctx.get("date_from")

        # Mapa código -> saldo inicial
        saldos_iniciales = self._dsc_compute_saldo_inicial(accounts, date_from)

        for row in account_res:
            code = row.get("code")
            row["saldo_inicial"] = saldos_iniciales.get(code, 0.0)
            # Saldo final = saldo inicial + movimiento del período (balance = debit-credit)
            row["saldo_final"] = row["saldo_inicial"] + row.get("balance", 0.0)
        return account_res

    def _dsc_compute_saldo_inicial(self, accounts, date_from):
        """Suma (debit - credit) de todos los apuntes contabilizados ANTES de date_from.

        Respeta el filtro de asientos (posted/all) y compañía del contexto original
        usando el mismo mecanismo que el kit, pero cambiando el rango de fechas a
        "todo lo anterior a date_from".
        """
        result = {}
        if not accounts:
            return result

        AML = self.env["account.move.line"]

        # Dominio: apuntes de estas cuentas, con fecha < date_from
        domain = [("account_id", "in", accounts.ids)]
        if date_from:
            domain.append(("date", "<", date_from))

        # Respetar el filtro de "asientos objetivo" (posted vs all) del contexto
        state = (self.env.context or {}).get("state")
        if state and state != "all":
            domain.append(("parent_state", "=", "posted"))

        # Agrupar por cuenta sumando debe y haber
        grouped = AML._read_group(
            domain,
            groupby=["account_id"],
            aggregates=["debit:sum", "credit:sum"],
        )
        # Mapear id de cuenta -> code
        id_to_code = {a.id: a.code for a in accounts}
        for account, debit, credit in grouped:
            code = id_to_code.get(account.id)
            if code is not None:
                result[code] = (debit or 0.0) - (credit or 0.0)
        return result
