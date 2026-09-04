# -*- coding: utf-8 -*-
"""
Integración con el web service de tipo de cambio oficial del
Banco Central de Nicaragua (BCN).

El servicio del BCN es un ASMX/SOAP antiguo que solo negocia TLS 1.0, por lo que
se usa un adaptador de requests con un SSLContext propio (minimum_version=TLSv1,
SECLEVEL=0). Esto aplica SOLO a la conexión con el BCN, no afecta al resto del sistema.

Contrato (verificado):
  URL:        https://servicios.bcn.gob.ni/Tc_Servicio/ServicioTC.asmx
  Método:     RecuperaTC_Mes(Ano, Mes)
  SOAPAction: http://servicios.bcn.gob.ni/RecuperaTC_Mes
  Respuesta:  <Tc><Fecha>YYYY-MM-DD</Fecha><Valor>36.6243</Valor>...</Tc>

Conversión a Odoo:
  El BCN entrega la tasa como NIO por 1 USD (ej. 36.6243).
  Odoo (moneda base NIO) guarda en res.currency.rate la tasa como USD por 1 NIO,
  es decir el inverso: 1 / 36.6243.
"""
import logging
import ssl
from datetime import date

from lxml import etree

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

BCN_URL = "https://servicios.bcn.gob.ni/Tc_Servicio/ServicioTC.asmx"
BCN_SOAP_ACTION = "http://servicios.bcn.gob.ni/RecuperaTC_Mes"
BCN_NS = "http://servicios.bcn.gob.ni/"


def _build_tls_session():
    """Sesión requests que fuerza TLS 1.0 solo para el BCN."""
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.poolmanager import PoolManager

    class _BcnTLSAdapter(HTTPAdapter):
        def init_poolmanager(self, *args, **kwargs):
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ctx.minimum_version = ssl.TLSVersion.TLSv1
            ctx.set_ciphers("DEFAULT@SECLEVEL=0")
            kwargs["ssl_context"] = ctx
            self.poolmanager = PoolManager(*args, **kwargs)

    session = requests.Session()
    session.mount("https://", _BcnTLSAdapter())
    return session


class ResCurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    origen_bcn = fields.Boolean(
        string="Origen BCN",
        default=False,
        help="Marca las tasas importadas automáticamente del Banco Central de Nicaragua.",
    )


class ResCurrency(models.Model):
    _inherit = "res.currency"

    # ------------------------------------------------------------------
    # Llamada SOAP al BCN
    # ------------------------------------------------------------------
    @api.model
    def _bcn_fetch_month(self, anio, mes):
        """Devuelve lista de tuplas (date, float) con las tasas NIO/USD del mes."""
        soap_envelope = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
            '<soap:Body>'
            '<RecuperaTC_Mes xmlns="%s">'
            '<Ano>%d</Ano><Mes>%d</Mes>'
            '</RecuperaTC_Mes>'
            '</soap:Body></soap:Envelope>'
        ) % (BCN_NS, int(anio), int(mes))

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": BCN_SOAP_ACTION,
        }
        try:
            session = _build_tls_session()
            resp = session.post(
                BCN_URL,
                data=soap_envelope.encode("utf-8"),
                headers=headers,
                timeout=30,
            )
        except Exception as e:
            _logger.error("BCN: error de conexión: %s", e)
            raise UserError(_(
                "No se pudo conectar al servicio del BCN.\n\nDetalle: %s"
            ) % e)

        if resp.status_code != 200:
            _logger.error("BCN: HTTP %s: %s", resp.status_code, resp.text[:500])
            raise UserError(_(
                "El BCN respondió con un error HTTP %s."
            ) % resp.status_code)

        return self._bcn_parse_response(resp.content)

    @api.model
    def _bcn_parse_response(self, xml_bytes):
        """Parsea los elementos <Tc> (Fecha, Valor). Devuelve [(date, float), ...]."""
        result = []
        try:
            root = etree.fromstring(xml_bytes)
        except Exception as e:
            _logger.error("BCN: XML inválido: %s", e)
            raise UserError(_("La respuesta del BCN no es un XML válido."))

        # localname 'Tc' sin importar namespace
        tc_nodes = [el for el in root.iter() if etree.QName(el).localname == "Tc"]
        for tc in tc_nodes:
            fecha_val = valor_val = None
            for child in tc:
                ln = etree.QName(child).localname
                if ln == "Fecha":
                    fecha_val = (child.text or "").strip()
                elif ln == "Valor":
                    valor_val = (child.text or "").strip()
            if not fecha_val or not valor_val:
                continue
            try:
                f = fields.Date.to_date(fecha_val)
                v = float(valor_val)
            except Exception:
                continue
            if f and v > 0:
                result.append((f, v))
        return result

    # ------------------------------------------------------------------
    # Actualizar tasas en Odoo
    # ------------------------------------------------------------------
    @api.model
    def _bcn_get_usd(self):
        usd = self.search([("name", "=", "USD")], limit=1)
        if not usd:
            raise UserError(_(
                "No existe la moneda USD. Actívela en Contabilidad → "
                "Configuración → Monedas antes de importar tasas del BCN."
            ))
        if not usd.active:
            usd.active = True
        return usd

    @api.model
    def bcn_importar_mes(self, anio=None, mes=None):
        """Importa las tasas del BCN de un mes y las guarda en res.currency.rate del USD.

        El BCN da NIO/USD; Odoo guarda USD/NIO (inverso).
        Retorna cantidad de tasas creadas/actualizadas.
        """
        hoy = date.today()
        anio = int(anio or hoy.year)
        mes = int(mes or hoy.month)

        company = self.env.company
        if company.currency_id.name != "NIO":
            raise UserError(_(
                "La moneda de la compañía debe ser NIO para usar las tasas del BCN. "
                "Actual: %s"
            ) % company.currency_id.name)

        usd = self._bcn_get_usd()
        tasas = self._bcn_fetch_month(anio, mes)
        if not tasas:
            raise UserError(_(
                "El BCN no devolvió tasas para %s/%s."
            ) % (mes, anio))

        Rate = self.env["res.currency.rate"]
        creadas = 0
        for fecha, valor_nio_usd in tasas:
            rate_odoo = 1.0 / valor_nio_usd  # USD por 1 NIO
            existing = Rate.search([
                ("currency_id", "=", usd.id),
                ("name", "=", fecha),
                ("company_id", "in", [company.id, False]),
            ], limit=1)
            vals = {
                "currency_id": usd.id,
                "name": fecha,
                "rate": rate_odoo,
                "company_id": company.id,
                "origen_bcn": True,
            }
            if existing:
                existing.write(vals)
            else:
                Rate.create(vals)
            creadas += 1

        _logger.info("BCN: %s tasas importadas para %s/%s", creadas, mes, anio)
        return creadas

    # ------------------------------------------------------------------
    # Punto de entrada del cron (importa el mes actual)
    # ------------------------------------------------------------------
    @api.model
    def _cron_bcn_actualizar_tasas(self):
        try:
            n = self.bcn_importar_mes()
            _logger.info("Cron BCN: %s tasas actualizadas.", n)
        except Exception as e:
            _logger.warning("Cron BCN: no se pudieron actualizar las tasas: %s", e)
