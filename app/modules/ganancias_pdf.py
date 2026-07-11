from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)


def _formato_moneda(valor):
    try:
        valor = float(valor or 0)
    except (TypeError, ValueError):
        valor = 0.0
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"$ {texto}"


def _formato_fecha_iso(fecha_str):
    if not fecha_str:
        return ""
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return fecha_str


def generar_pdf_ganancias(
    fecha_desde: str,
    fecha_hasta: str,
    pedidos,
    total_gastos: float,
    total_ganancia: float,
    ganancia_neta: float,
    top_proveedores,
    top_productos,
    ruta_salida: str,
):
    doc = SimpleDocTemplate(
        str(ruta_salida),
        pagesize=A4,
        topMargin=18 * mm,
        bottomMargin=15 * mm,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TituloReporte", parent=styles["Title"], fontSize=18, spaceAfter=2,
    )
    subtitle_style = ParagraphStyle(
        "Subtitulo", parent=styles["Normal"], fontSize=10, textColor=colors.HexColor("#555555"),
    )
    section_style = ParagraphStyle(
        "Seccion", parent=styles["Heading2"], fontSize=13, spaceBefore=14, spaceAfter=6,
        textColor=colors.HexColor("#2a2a2a"),
    )
    right_style = ParagraphStyle("Right", parent=styles["Normal"], alignment=TA_RIGHT)

    elementos = []

    # ---- Encabezado ----
    elementos.append(Paragraph("Reporte de Ganancias", title_style))
    elementos.append(Paragraph(
        f"Período: {_formato_fecha_iso(fecha_desde)} — {_formato_fecha_iso(fecha_hasta)}"
        f"&nbsp;&nbsp;|&nbsp;&nbsp;Emitido: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        subtitle_style,
    ))
    elementos.append(Spacer(1, 10 * mm))

    # ---- Resumen ----
    elementos.append(Paragraph("Resumen", section_style))
    resumen_data = [
        ["Gastos", _formato_moneda(total_gastos)],
        ["Ganancia", _formato_moneda(total_ganancia)],
        ["Ganancia Neta", _formato_moneda(ganancia_neta)],
    ]
    resumen_tabla = Table(resumen_data, colWidths=[80 * mm, 40 * mm])
    resumen_tabla.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TEXTCOLOR", (0, 2), (-1, 2),
            colors.HexColor("#1a7a3c") if ganancia_neta >= 0 else colors.HexColor("#b91c1c")),
        ("LINEABOVE", (0, 2), (-1, 2), 0.75, colors.HexColor("#999999")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
    ]))
    elementos.append(resumen_tabla)

    # ---- Top proveedores ----
    top_proveedores = list(top_proveedores)
    if top_proveedores:
        elementos.append(Paragraph("Top proveedores con más gasto", section_style))
        data = [["#", "Proveedor", "Total"]]
        for i, row in enumerate(top_proveedores, start=1):
            data.append([str(i), str(row["proveedor"]), _formato_moneda(row["total"])])
        tabla = Table(data, colWidths=[10 * mm, 110 * mm, 40 * mm])
        tabla.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2a2a2a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (2, 0), (2, -1), "RIGHT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")),
        ]))
        elementos.append(tabla)

    # ---- Top productos/trabajos ----
    top_productos = list(top_productos)
    if top_productos:
        elementos.append(Paragraph("Top trabajos más realizados", section_style))
        data = [["#", "Trabajo", "Cantidad", "Total"]]
        for i, row in enumerate(top_productos, start=1):
            data.append([
                str(i), str(row["producto"]), str(row["cantidad"]), _formato_moneda(row["total"])
            ])
        tabla = Table(data, colWidths=[10 * mm, 90 * mm, 25 * mm, 35 * mm])
        tabla.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2a2a2a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (2, 0), (3, -1), "RIGHT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")),
        ]))
        elementos.append(tabla)

    # ---- Tabla completa de trabajos del período ----
    pedidos = list(pedidos)
    elementos.append(Paragraph(f"Trabajos del período ({len(pedidos)})", section_style))
    if pedidos:
        data = [["Cliente", "Trabajo", "Fecha ingreso", "Total"]]
        for p in pedidos:
            data.append([
                str(p["cliente"]),
                str(p["tipo_trabajo"]),
                _formato_fecha_iso(p["fecha_ingreso"]),
                _formato_moneda(p["precio_final"] or 0),
            ])
        tabla = Table(data, colWidths=[55 * mm, 55 * mm, 30 * mm, 30 * mm], repeatRows=1)
        tabla.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2a2a2a")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (3, 0), (3, -1), "RIGHT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")),
        ]))
        elementos.append(tabla)
    else:
        elementos.append(Paragraph("No hay trabajos cargados en este período.", styles["Normal"]))

    doc.build(elementos)
    return str(ruta_salida)