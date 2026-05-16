"""
Configuración central de la aplicación.
Ajustá los valores antes de usar en producción.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ─── AFIP / ARCA ────────────────────────────────────────────────────────────
AFIP_CUIT         = "20123456789"           # CUIT del emisor
AFIP_PUNTO_VENTA  = 1                       # Número de punto de venta
AFIP_CERT         = BASE_DIR / "certs" / "cert.crt"
AFIP_KEY          = BASE_DIR / "certs" / "private.key"
AFIP_PASSPHRASE   = ""                      # Passphrase de la clave privada (si tiene)

# Ambiente: "homologacion" o "produccion"
AFIP_AMBIENTE = os.getenv("AFIP_AMBIENTE", "homologacion")

WSAA_URLS = {
    "homologacion": "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl",
    "produccion":   "https://wsaa.afip.gov.ar/ws/services/LoginCms?wsdl",
}

WSFE_URLS = {
    "homologacion": "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL",
    "produccion":   "https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL",
}

# ─── BASE DE DATOS ───────────────────────────────────────────────────────────
DATABASE_URL = f"sqlite:///{BASE_DIR / 'facturacion.db'}"

# ─── EMPRESA (para el PDF) ───────────────────────────────────────────────────
EMPRESA_NOMBRE        = "Mi Empresa S.R.L."
EMPRESA_DOMICILIO     = "Av. Siempreviva 742, Buenos Aires"
EMPRESA_CONDICION_IVA = "Responsable Inscripto"
EMPRESA_INICIO_ACTIVIDADES = "01/01/2020"
EMPRESA_INGRESOS_BRUTOS    = "123-456789-0"

# ─── COMPROBANTES ────────────────────────────────────────────────────────────
TIPOS_COMPROBANTE = {
    1:  "Factura A",
    6:  "Factura B",
    11: "Factura C",
    51: "Factura M",
}

CONDICIONES_IVA = {
    "RI": "Responsable Inscripto",
    "MO": "Monotributista",
    "EX": "Exento",
    "CF": "Consumidor Final",
}

ALICUOTAS_IVA = {
    0:    0.00,
    3:    0.00,   # exento
    4:   10.50,
    5:   21.00,
    6:   27.00,
    8:    5.00,
    9:    2.50,
}