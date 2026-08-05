"""
Generador de PDF para "Presupuesto" (A4 vertical, plantilla Intermedios).
"""

import sys
from pathlib import Path
from datetime import datetime
from textwrap import wrap

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def get_base_path():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent.parent


TEMPLATE_PATH = get_base_path() / "assets" / "presupuesto_template.png"

TEMPLATE_PX_WIDTH = 1122
TEMPLATE_PX_HEIGHT = 1600

PAGE_SIZE = A4
PAGE_W, PAGE_H = PAGE_SIZE

SCALE_X = PAGE_W / TEMPLATE_PX_WIDTH
SCALE_Y = PAGE_H / TEMPLATE_PX_HEIGHT


def _px(x, y):
    return x * SCALE_X, PAGE_H - (y * SCALE_Y)


def _formato_moneda(valor):
    try:
        valor = float(valor or 0)
    except (TypeError, ValueError):
        valor = 0.0
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"$ {texto}"


def _formato_fecha(fecha_str):
    if not fecha_str:
        return ""
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return fecha_str


def generar_pdf_presupuesto(presupuesto, ruta_salida):
    """
    presupuesto: dict o sqlite3.Row con las claves:
        id_presupuesto, cliente, telefono_cliente, direccion_cliente,
        tipo_trabajo, descripcion, total, fecha_ingreso, fecha_expiracion
    """
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"No se encontro la plantilla en: {TEMPLATE_PATH}")

    def get(campo, default=""):
        try:
            valor = presupuesto[campo]
        except (KeyError, IndexError, TypeError):
            valor = None
        return valor if valor not in (None, "") else default

    c = canvas.Canvas(str(ruta_salida), pagesize=PAGE_SIZE)
    c.drawImage(str(TEMPLATE_PATH), 0, 0, width=PAGE_W, height=PAGE_H)
    c.setFillColorRGB(0.15, 0.15, 0.15)

    # N de presupuesto (dentro de la barra marron, en blanco)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 15)
    x, y = _px(440, 262)
    c.drawRightString(x, y, f"{int(get('id_presupuesto', 0)):04d}")
    c.setFillColorRGB(0.15, 0.15, 0.15)

    # Cliente
    c.setFont("Helvetica", 13)
    x, y = _px(110, 363)
    c.drawString(x, y, str(get("cliente")))

    # Telefono
    x, y = _px(895, 363)
    c.drawString(x, y, str(get("telefono_cliente")))

    # Domicilio
    x, y = _px(130, 412)
    c.drawString(x, y, str(get("direccion_cliente")))

    # Categoria (tipo de trabajo)
    c.setFont("Helvetica", 13)
    x, y = _px(75, 632)
    c.drawString(x, y, str(get("tipo_trabajo")))

# Detalle (con el total al final, ya que la plantilla no tiene renglon aparte)
    c.setFont("Helvetica", 12)
    detalle = str(get("descripcion"))
    lineas = []
    if detalle:
        for parrafo in detalle.splitlines():
            if parrafo.strip() == "":
                lineas.append("")
            else:
                lineas.extend(wrap(parrafo, width=95))
    x, y = _px(70, 715)
    for linea in lineas[:28]:
        c.drawString(x, y, linea)
        y -= 17

    total = get("total", 0)
    c.setFont("Helvetica-Bold", 13)
    y -= 10
    c.drawString(x, y, f"Total: {_formato_moneda(total)}")

    # Fecha de presupuesto
    c.setFont("Helvetica-Bold", 13)
    x, y = _px(651, 278)
    c.drawCentredString(x, y, _formato_fecha(get("fecha_ingreso")))

    # Vigente hasta
    x, y = _px(922, 280)
    c.drawCentredString(x, y, _formato_fecha(get("fecha_expiracion")))

    c.save()
    return str(ruta_salida)