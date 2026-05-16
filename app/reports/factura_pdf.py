"""
Generador de PDF de factura electrónica con formato AFIP/ARCA.
Usa los datos del emisor y cliente tal como vienen de db.py (sqlite3.Row).
"""

import base64
import json
from pathlib import Path

import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, Image as RLImage, Paragraph,
    SimpleDocTemplate, Spacer, Table, TableStyle,
)

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "facturas_pdf"
OUTPUT_DIR.mkdir(exist_ok=True)

TIPOS_COMPROBANTE = {
    "Factura A": "A",
    "Factura B": "B",
    "Factura C": "C",
    "Factura M": "M",
}

TIPOS_CBTE_ID = {"Factura A": 1, "Factura B": 6, "Factura C": 11, "Factura M": 51}


def _qr_url(factura, emisor) -> str:
    cuit = int(str(emisor["cuit"]).replace("-", ""))
    fecha = str(factura["fecha"]).replace("-", "")
    data = {
        "ver":    1,
        "fecha":  f"{fecha[:4]}-{fecha[4:6]}-{fecha[6:]}",
        "cuit":   cuit,
        "ptoVta": int(factura["punto_venta"] or 1),
        "tipoCmp": TIPOS_CBTE_ID.get(factura["tipo_comprobante"], 6),
        "nroCmp": int(factura["numero"] or 0),
        "importe": float(factura["total"] or 0),
        "moneda": "PES",
        "ctz":    1,
        "tipoDocRec": 80,
        "nroDocRec":  0,
        "tipoCodAut": "E",
        "codAut":     int(factura["cae"] or 0),
    }
    return "https://www.afip.gob.ar/fe/qr/?p=" + base64.b64encode(
        json.dumps(data).encode()
    ).decode()


def _make_qr(url: str) -> str:
    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    path = OUTPUT_DIR / "_qr_tmp.png"
    img.save(path)
    return str(path)


def generar_pdf(factura, cliente, emisor, detalles: list) -> str:
    """
    Genera el PDF de la factura.
    factura, cliente, emisor: sqlite3.Row o dict
    detalles: lista de dicts con descripcion, cantidad, precio_unitario, iva, subtotal
    Devuelve la ruta del PDF generado.
    """
    pv  = str(factura["punto_venta"] or 1).zfill(4)
    num = str(factura["numero"] or 0).zfill(8)
    filename = OUTPUT_DIR / f"factura_{pv}-{num}.pdf"

    doc = SimpleDocTemplate(
        str(filename), pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
    )

    styles  = getSampleStyleSheet()
    normal  = styles["Normal"]
    bold    = ParagraphStyle("bold",   parent=normal, fontName="Helvetica-Bold")
    small   = ParagraphStyle("small",  parent=normal, fontSize=8)
    big_c   = ParagraphStyle("bigc",   parent=normal, alignment=1, fontSize=22, fontName="Helvetica-Bold")

    letra       = TIPOS_COMPROBANTE.get(factura["tipo_comprobante"], "?")
    tipo_nombre = factura["tipo_comprobante"] or "Comprobante"

    # Nombre del cliente
    if cliente["tipo_cliente"] == "Empresa":
        nombre_cliente = cliente["nombre_empresa"] or ""
    else:
        nombre_cliente = f"{cliente['nombre'] or ''} {cliente['apellido'] or ''}".strip()

    elements = []

    # ── Encabezado ────────────────────────────────────────────────────────────
    razon = emisor["razon_social"] or ""
    domicilio_emisor = emisor["domicilio"] or ""
    cond_iva_emisor  = emisor["condicion_iva"] or ""
    cuit_emisor      = emisor["cuit"] or ""
    iibb             = emisor["ingresos_brutos"] or ""
    inicio_act       = emisor["inicio_actividades"] or ""
    pv_str           = str(factura["punto_venta"] or 1).zfill(4)

    fecha_str = str(factura["fecha"] or "")

    header = [
        [Paragraph(f"<b>{razon}</b>", bold), Paragraph(letra, big_c), Paragraph(f"<b>{tipo_nombre}</b>", bold)],
        [Paragraph(domicilio_emisor, normal), "", Paragraph(f"N° {pv}-{num}", normal)],
        [Paragraph(f"Cond. IVA: {cond_iva_emisor}", normal), "", Paragraph(f"Fecha: {fecha_str}", normal)],
        [Paragraph(f"CUIT: {cuit_emisor}", normal), "", Paragraph(f"Punto de venta: {pv_str}", normal)],
        [Paragraph(f"Ing. Brutos: {iibb}", normal), "", Paragraph(f"Inicio act.: {inicio_act}", normal)],
    ]
    t_header = Table(header, colWidths=[8*cm, 2*cm, 8*cm])
    t_header.setStyle(TableStyle([
        ("BOX",       (0, 0), (-1, -1), 1, colors.black),
        ("LINEAFTER", (0, 0), (0, -1),  1, colors.black),
        ("LINEAFTER", (1, 0), (1, -1),  1, colors.black),
        ("ALIGN",     (1, 0), (1, -1),  "CENTER"),
        ("VALIGN",    (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 0.4*cm))

    # ── Receptor ──────────────────────────────────────────────────────────────
    receptor = [
        [Paragraph(f"<b>Cliente:</b> {nombre_cliente}", normal),
         Paragraph(f"<b>CUIT/CUIL:</b> {cliente['cuil'] or cliente.get('dni','')}", normal)],
        [Paragraph(f"<b>Domicilio:</b> {cliente['direccion'] or ''}, {cliente['localidad'] or ''}", normal),
         Paragraph(f"<b>Cond. IVA:</b> {cliente['condicion_iva'] or ''}", normal)],
    ]
    t_receptor = Table(receptor, colWidths=[9*cm, 9*cm])
    t_receptor.setStyle(TableStyle([
        ("BOX",  (0, 0), (-1, -1), 1, colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_receptor)
    elements.append(Spacer(1, 0.4*cm))

    # ── Ítems ─────────────────────────────────────────────────────────────────
    rows = [["Descripción", "Cant.", "Precio Unit.", "IVA %", "Subtotal"]]
    for d in detalles:
        rows.append([
            d.get("descripcion", ""),
            f"{float(d.get('cantidad', 1)):.2f}",
            f"$ {float(d.get('precio_unitario', 0)):.2f}",
            f"{float(d.get('iva', 0)):.1f}%",
            f"$ {float(d.get('subtotal', 0)):.2f}",
        ])
    t_items = Table(rows, colWidths=[7.5*cm, 2*cm, 3*cm, 2*cm, 3.5*cm])
    t_items.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  colors.HexColor("#1e293b")),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("ALIGN",          (1, 0), (-1, -1), "RIGHT"),
        ("GRID",           (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
        ("TOPPADDING",     (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_items)
    elements.append(Spacer(1, 0.4*cm))

    # ── Totales ───────────────────────────────────────────────────────────────
    subtotal = float(factura["subtotal"] or 0)
    iva_val  = float(factura["iva"] or 0)
    total    = float(factura["total"] or 0)

    t_totales = Table([
        ["", "Neto gravado:", f"$ {subtotal:.2f}"],
        ["", "IVA:",          f"$ {iva_val:.2f}"],
        ["", "TOTAL:",        f"$ {total:.2f}"],
    ], colWidths=[10*cm, 4*cm, 4*cm])
    t_totales.setStyle(TableStyle([
        ("ALIGN",    (1, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (1, 2), (-1, 2),  "Helvetica-Bold"),
        ("FONTSIZE", (1, 2), (-1, 2),  12),
        ("LINEABOVE",(1, 2), (-1, 2),  1, colors.black),
    ]))
    elements.append(t_totales)
    elements.append(Spacer(1, 0.4*cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    elements.append(Spacer(1, 0.3*cm))

    # ── CAE + QR ──────────────────────────────────────────────────────────────
    if factura.get("cae"):
        qr_path = _make_qr(_qr_url(factura, emisor))
        vto_cae = str(factura.get("vencimiento_cae") or "")

        t_cae = Table([
            [Paragraph(f"<b>CAE N°:</b> {factura['cae']}", normal),
             RLImage(qr_path, width=2.5*cm, height=2.5*cm)],
            [Paragraph(f"<b>Vto. CAE:</b> {vto_cae}", normal), ""],
        ], colWidths=[15*cm, 3*cm])
        t_cae.setStyle(TableStyle([
            ("BOX",    (0, 0), (-1, -1), 1, colors.black),
            ("SPAN",   (1, 0), (1, 1)),
            ("VALIGN", (1, 0), (1, 1), "MIDDLE"),
            ("ALIGN",  (1, 0), (1, 1), "CENTER"),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(t_cae)

    doc.build(elements)

    try:
        (OUTPUT_DIR / "_qr_tmp.png").unlink(missing_ok=True)
    except Exception:
        pass

    return str(filename)