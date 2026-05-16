"""
Servicio WSFEv1 — Factura Electrónica AFIP/ARCA.
Recibe todos los parámetros del emisor desde la BD (no de settings.py),
para que el usuario los configure desde la vista Emisor.
"""

import os
from datetime import date

from zeep import Client as ZeepClient

from app.services.wsaa import get_token_sign

WSFE_URLS = {
    "homologacion": "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL",
    "produccion":   "https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL",
}

def _ambiente():
    return os.getenv("AFIP_AMBIENTE", "homologacion")

def _client():
    return ZeepClient(WSFE_URLS[_ambiente()])

def _auth(cuit: str):
    token, sign = get_token_sign(cuit)
    return {"Token": token, "Sign": sign, "Cuit": int(cuit.replace("-", ""))}


def ultimo_comprobante(cuit: str, punto_venta: int, tipo_cbte: int) -> int:
    """Devuelve el último número de comprobante autorizado."""
    client = _client()
    resp = client.service.FECompUltimoAutorizado(
        Auth=_auth(cuit),
        PtoVta=punto_venta,
        CbteTipo=tipo_cbte,
    )
    return resp.CbteNro


def autorizar_factura(
    emisor_cuit: str,
    punto_venta: int,
    tipo_cbte: int,
    cliente_cuit: str,
    imp_neto: float,
    imp_iva: float,
    imp_total: float,
    alicuotas: list,
    concepto: int = 1,
) -> dict:
    """
    Solicita CAE a ARCA/AFIP.
    Returns: dict con numero, cae, cae_vto, resultado, observaciones.
    """
    client  = _client()
    cuit_limpio = emisor_cuit.replace("-", "")
    numero  = ultimo_comprobante(emisor_cuit, punto_venta, tipo_cbte) + 1
    hoy     = date.today().strftime("%Y%m%d")

    doc_nro  = int(cliente_cuit.replace("-", ""))
    doc_tipo = 80 if len(str(doc_nro)) == 11 else 96  # 80=CUIT, 96=DNI

    iva_array = [
        {
            "AlicIva": {
                "Id":      a["Id"],
                "BaseImp": round(a["BaseImp"], 2),
                "Importe": round(a["Importe"], 2),
            }
        }
        for a in alicuotas
    ]

    fe_cab = {
        "CantReg":  1,
        "PtoVta":   punto_venta,
        "CbteTipo": tipo_cbte,
    }

    fe_det = {
        "FECAEDetRequest": {
            "Concepto":   concepto,
            "DocTipo":    doc_tipo,
            "DocNro":     doc_nro,
            "CbteDesde":  numero,
            "CbteHasta":  numero,
            "CbteFch":    hoy,
            "ImpTotal":   round(imp_total, 2),
            "ImpTotConc": 0.00,
            "ImpNeto":    round(imp_neto, 2),
            "ImpOpEx":    0.00,
            "ImpIVA":     round(imp_iva, 2),
            "ImpTrib":    0.00,
            "MonId":      "PES",
            "MonCotiz":   1,
            "Iva":        iva_array if iva_array else None,
        }
    }

    resp = client.service.FECAESolicitar(
        Auth=_auth(emisor_cuit),
        FeCAEReq={"FeCabReq": fe_cab, "FeDetReq": fe_det},
    )

    det = resp.FeDetResp.FECAEDetResponse[0]

    observaciones = []
    if det.Observaciones:
        for obs in det.Observaciones.Obs:
            observaciones.append(f"[{obs.Code}] {obs.Msg}")

    return {
        "numero":        numero,
        "cae":           det.CAE if det.Resultado == "A" else None,
        "cae_vto":       det.CAEFchVto if det.Resultado == "A" else None,
        "resultado":     det.Resultado,
        "observaciones": "\n".join(observaciones),
    }