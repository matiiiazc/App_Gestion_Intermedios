"""
Servicio WSAA — Autenticación con ARCA/AFIP.
Lee el certificado desde la carpeta certs/ del proyecto.
El token se cachea por 12 horas para no re-autenticar en cada factura.
"""

import base64
import hashlib
import pickle
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs7
from zeep import Client as ZeepClient

import os

WSAA_URLS = {
    "homologacion": "https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl",
    "produccion":   "https://wsaa.afip.gov.ar/ws/services/LoginCms?wsdl",
}

_CERTS_DIR  = Path(__file__).resolve().parent.parent.parent / "certs"
_CACHE_FILE = Path(__file__).resolve().parent.parent.parent / ".wsaa_cache.pkl"
_SERVICE    = "wsfe"


def _ambiente():
    return os.getenv("AFIP_AMBIENTE", "homologacion")


def _build_tra() -> bytes:
    now = datetime.now(timezone.utc)
    uid = hashlib.sha1(str(now.timestamp()).encode()).hexdigest()[:8]
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<loginTicketRequest version="1.0">
  <header>
    <uniqueId>{uid}</uniqueId>
    <generationTime>{now.strftime('%Y-%m-%dT%H:%M:%S')}-00:00</generationTime>
    <expirationTime>{now.strftime('%Y-%m-%dT%H:%M:%S')}-00:00</expirationTime>
  </header>
  <service>{_SERVICE}</service>
</loginTicketRequest>""".encode("utf-8")


def _sign_tra(tra: bytes) -> str:
    cert_path = _CERTS_DIR / "cert.crt"
    key_path  = _CERTS_DIR / "private.key"

    if not cert_path.exists() or not key_path.exists():
        raise FileNotFoundError(
            f"No se encontraron los archivos de certificado en {_CERTS_DIR}.\n"
            "Necesitás colocar cert.crt y private.key en la carpeta certs/."
        )

    with open(key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)

    with open(cert_path, "rb") as f:
        cert = x509.load_pem_x509_certificate(f.read())

    signed = (
        pkcs7.PKCS7SignatureBuilder()
        .set_data(tra)
        .add_signer(cert, private_key, hashes.SHA256())
        .sign(serialization.Encoding.DER, [pkcs7.PKCS7Options.DetachedSignature])
    )
    return base64.b64encode(signed).decode()


def _load_cache(cuit: str):
    if not _CACHE_FILE.exists():
        return None
    try:
        with open(_CACHE_FILE, "rb") as f:
            data = pickle.load(f)
        entry = data.get(cuit)
        if not entry:
            return None
        expiry = datetime.fromisoformat(entry["expiry"])
        if datetime.now(timezone.utc) < expiry:
            return entry
    except Exception:
        pass
    return None


def _save_cache(cuit: str, token: str, sign: str, expiry: str):
    data = {}
    if _CACHE_FILE.exists():
        try:
            with open(_CACHE_FILE, "rb") as f:
                data = pickle.load(f)
        except Exception:
            pass
    data[cuit] = {"token": token, "sign": sign, "expiry": expiry}
    with open(_CACHE_FILE, "wb") as f:
        pickle.dump(data, f)


def get_token_sign(cuit: str):
    """
    Devuelve (token, sign) para el CUIT dado.
    Reutiliza caché si el TA todavía no expiró (válido 12hs).
    """
    cached = _load_cache(cuit)
    if cached:
        return cached["token"], cached["sign"]

    tra = _build_tra()
    cms = _sign_tra(tra)

    client   = ZeepClient(WSAA_URLS[_ambiente()])
    response = client.service.loginCms(in0=cms)

    root   = ET.fromstring(response)
    token  = root.find(".//token").text
    sign   = root.find(".//sign").text
    expiry = root.find(".//expirationTime").text

    _save_cache(cuit, token, sign, expiry)
    return token, sign