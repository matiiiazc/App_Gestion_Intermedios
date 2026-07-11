"""
Generador de PDF para la "Orden de pedido" (formato A5, plantilla Intermedios).

Dibuja los datos del pedido sobre la imagen de la plantilla usando ReportLab.
"""

import sys
from pathlib import Path
from datetime import datetime
from textwrap import wrap

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5, landscape


def get_base_path():
    """Misma lógica que en app/db.py: carpeta del ejecutable si está
    empaquetado (PyInstaller), o raíz del proyecto en desarrollo."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent.parent


TEMPLATE_PATH = get_base_path() / "assets" / "orden_pedido_template.png"

# Tamaño de referencia de la plantilla (pixeles) usado para calcular las
# posiciones del texto. Si se reemplaza la imagen por otra de distinto
# tamaño, hay que actualizar estos valores.
TEMPLATE_PX_WIDTH = 790
TEMPLATE_PX_HEIGHT = 558

PAGE_SIZE = landscape(A5)
PAGE_W, PAGE_H = PAGE_SIZE

SCALE_X = PAGE_W / TEMPLATE_PX_WIDTH
SCALE_Y = PAGE_H / TEMPLATE_PX_HEIGHT


def _px(x, y):
    """Convierte coordenadas en pixeles de la plantilla (origen arriba-izq)
    a puntos de ReportLab (origen abajo-izq)."""
    return x * SCALE_X, PAGE_H - (y * SCALE_Y)


def _formato_moneda(valor):
    try:
        valor = float(valor or 0)
    except (TypeError, ValueError):
        valor = 0.0
    texto = f"{valor:,.2f}"
    # 1,234.56 -> 1.234,56 (formato argentino)
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"$ {texto}"


def _formato_fecha(fecha_str):
    if not fecha_str:
        return ""
    try:
        return datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return fecha_str


def generar_pdf_orden_pedido(pedido, ruta_salida):
  
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"No se encontro la plantilla en: {TEMPLATE_PATH}")

    def get(campo, default=""):
        try:
            valor = pedido[campo]
        except (KeyError, IndexError, TypeError):
            valor = None
        return valor if valor not in (None, "") else default

    total = float(get("precio_final", 0) or 0)
    sena = float(get("sena", 0) or 0)
    saldo = total - sena

    c = canvas.Canvas(str(ruta_salida), pagesize=PAGE_SIZE)
    c.drawImage(str(TEMPLATE_PATH), 0, 0, width=PAGE_W, height=PAGE_H)
    c.setFillColorRGB(0, 0, 0)

    # N de pedido
    c.setFont("Helvetica-Bold", 13)
    x, y = _px(745, 45)
    c.drawCentredString(x, y, f"{int(get('id_pedido', 0)):04d}")

    # Cliente
    c.setFont("Helvetica", 13)
    x, y = _px(95, 120)
    c.drawString(x, y, str(get("cliente")))

    # Telefono
    c.setFont("Helvetica-Bold", 13)
    x, y = _px(478, 120)
    c.drawString(x, y, str(get("telefono_cliente")))

    # Domicilio
    c.setFont("Helvetica-Bold", 13)
    x, y = _px(100, 151)
    c.drawString(x, y, str(get("direccion_cliente")))

    # Categoria (tipo de trabajo)
    c.setFont("Helvetica-Bold", 13)
    x, y = _px(120, 189)
    c.drawString(x, y, str(get("tipo_trabajo")))

    # Detalle (descripcion, con salto de linea automatico)
    c.setFont("Helvetica", 13)
    detalle = str(get("descripcion"))
    lineas = wrap(detalle, width=95) if detalle else []
    x, y = _px(20, 240)
    max_lineas = 7  # limite para no salirse del recuadro
    for linea in lineas[:max_lineas]:
        c.drawString(x, y, linea)
        y -= 12

    # Fecha de pedido
    c.setFont("Helvetica-Bold", 13)
    x, y = _px(684, 133)
    c.drawCentredString(x, y, _formato_fecha(get("fecha_ingreso")))

    # Fecha de entrega
    x, y = _px(684, 187)
    c.drawCentredString(x, y, _formato_fecha(get("fecha")))

    # Total
    c.setFont("Helvetica-Bold", 13)
    x, y = _px(104, 362)
    c.drawCentredString(x, y, _formato_moneda(total))

    # Sena
    c.setFont("Helvetica-Bold", 13)
    x, y = _px(293, 362)
    c.drawCentredString(x, y, _formato_moneda(sena))

    # Saldo
    c.setFont("Helvetica-Bold", 13)
    x, y = _px(477, 362)
    c.drawCentredString(x, y, _formato_moneda(saldo))

    c.save()
    return str(ruta_salida)