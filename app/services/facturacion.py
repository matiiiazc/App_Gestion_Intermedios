"""
Servicio principal de facturación.
Orquesta: autenticación WSAA → emisión WSFEv1 → actualización BD → generación PDF.
"""

from app.db import Database
from app.services.wsfe import autorizar_factura as wsfe_autorizar
from app.reports.factura_pdf import generar_pdf


# Mapa tipo_comprobante (texto) → código AFIP
TIPO_CBTE = {
    "Factura A": 1,
    "Factura B": 6,
    "Factura C": 11,
    "Factura M": 51,
}

# Mapa alícuota IVA (%) → ID AFIP
ALICUOTA_ID = {
    0.0:  3,
    10.5: 4,
    21.0: 5,
    27.0: 6,
    5.0:  8,
    2.5:  9,
}


def autorizar_y_generar_pdf(id_factura: int) -> dict:
    """
    Flujo completo para una factura guardada en la BD:
      1. Obtiene datos de la BD (factura, detalles, cliente, emisor).
      2. Llama a ARCA/AFIP para obtener el CAE.
      3. Actualiza la BD con número, CAE y vencimiento.
      4. Genera el PDF.
    Devuelve dict con 'cae', 'numero', 'pdf_path' o lanza excepción.
    """
    db = Database()
    try:
        factura = db.get_factura(id_factura)
        if not factura:
            raise ValueError(f"No se encontró la factura con id {id_factura}")

        detalles = db.get_factura_detalles(id_factura)
        cliente  = db.get_cliente(factura["cliente_id"])
        emisor   = db.get_emisor()

        if not emisor:
            raise ValueError("No hay datos del emisor configurados. Completá la sección Emisor.")

        # Construir alícuotas para WSFEv1
        alicuotas_agrupadas: dict[float, dict] = {}
        for d in detalles:
            pct  = float(d["iva"] or 0)
            base = float(d["subtotal"] or 0)
            imp  = round(base * pct / 100, 2)
            if pct not in alicuotas_agrupadas:
                alicuotas_agrupadas[pct] = {
                    "Id":      ALICUOTA_ID.get(pct, 5),
                    "BaseImp": 0.0,
                    "Importe": 0.0,
                }
            alicuotas_agrupadas[pct]["BaseImp"] += base
            alicuotas_agrupadas[pct]["Importe"] += imp

        alicuotas = list(alicuotas_agrupadas.values())

        tipo_cbte = TIPO_CBTE.get(factura["tipo_comprobante"])
        if tipo_cbte is None:
            raise ValueError(f"Tipo de comprobante desconocido: {factura['tipo_comprobante']}")

        cuit_emisor  = str(emisor["cuit"]).replace("-", "")
        punto_venta  = int(factura["punto_venta"] or emisor.get("punto_venta") or 1)
        cuit_cliente = str(cliente["cuil"] or cliente.get("dni") or "0").replace("-", "")

        resultado = wsfe_autorizar(
            emisor_cuit  = cuit_emisor,
            punto_venta  = punto_venta,
            tipo_cbte    = tipo_cbte,
            cliente_cuit = cuit_cliente,
            imp_neto     = float(factura["subtotal"] or 0),
            imp_iva      = float(factura["iva"] or 0),
            imp_total    = float(factura["total"] or 0),
            alicuotas    = alicuotas,
        )

        if resultado["resultado"] != "A":
            obs = resultado.get("observaciones", "Sin detalle")
            raise RuntimeError(f"ARCA rechazó la factura: {obs}")

        db.actualizar_factura_arca(
            id_factura,
            resultado["numero"],
            resultado["cae"],
            resultado["cae_vto"],
            "Autorizada",
        )

        # Refrescar factura con número y CAE ya guardados
        factura_actualizada = db.get_factura(id_factura)

        detalles_lista = [dict(d) for d in detalles]
        pdf_path = generar_pdf(
            factura  = factura_actualizada,
            cliente  = cliente,
            emisor   = emisor,
            detalles = detalles_lista,
        )

        return {
            "numero":   resultado["numero"],
            "cae":      resultado["cae"],
            "cae_vto":  resultado["cae_vto"],
            "pdf_path": pdf_path,
        }

    finally:
        db.cerrar()
