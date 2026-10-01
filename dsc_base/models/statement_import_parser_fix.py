# -*- coding: utf-8 -*-
"""
Parche para account_statement_import_sheet_file (OCA, recién migrado a 19.0).

BUG: en _parse_lines_csv, el conteo de filas usa:
    numrows = len(str(data_file.strip()).split("\\n"))
que sobre bytes da un conteo incorrecto (1 en vez de N), dejando footer_line=1
y descartando TODAS las filas de datos -> el import produce 0 transacciones y
muestra el engañoso "Ya ha importado este archivo...".

FIX: sobrescribimos _parse_lines_csv contando las filas reales del CSV decodificado.
No se toca el módulo de terceros; se corrige por herencia desde dsc_base.
"""
import logging
from io import StringIO
from csv import reader

from odoo import api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import chardet
except ImportError:
    chardet = None


class AccountStatementImportSheetParser(models.TransientModel):
    _inherit = "account.statement.import.sheet.parser"

    @api.model
    def _parse_lines_csv(self, mapping, data_file, currency_code):
        """Versión corregida: cuenta las filas reales en vez del str(bytes).split roto."""
        columns = dict()
        csv_options = {}
        csv_delimiter = mapping._get_column_delimiter_character()
        if csv_delimiter:
            csv_options["delimiter"] = csv_delimiter
        if mapping.quotechar:
            csv_options["quotechar"] = mapping.quotechar

        detected_encoding = (chardet.detect(data_file).get("encoding", False)
                             if chardet else "utf-8")
        if not detected_encoding:
            raise UserError(
                self.env._("No valid encoding was found for the attached file")
            ) from None
        decoded_file = data_file.decode(detected_encoding)

        # --- Conteo correcto de filas (FIX) ---
        # líneas no vacías del archivo decodificado
        numrows = len([ln for ln in decoded_file.splitlines() if ln.strip()])

        rows = reader(StringIO(decoded_file), **csv_options)
        header = self.parse_header_csv(rows, mapping)
        for column_name in self._get_column_names():
            columns[column_name] = self._get_column_indexes(
                header, column_name, mapping
            )

        label_line = mapping.header_lines_skip_count
        footer_line = numrows - mapping.footer_lines_skip_count
        data = rows, label_line, footer_line
        return self._parse_rows(mapping, currency_code, data, columns)
