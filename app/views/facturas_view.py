import os
import subprocess
import sys

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QFormLayout, QDialog, QDialogButtonBox,
    QComboBox, QDoubleSpinBox, QSpinBox, QLineEdit, QDateEdit, QTextEdit,
    QLabel
)
from PySide6.QtCore import Qt, QDate

from app.modules.facturas import FacturasModule


class FacturaDialog(QDialog):
    def __init__(self, parent=None, clientes=None, productos=None):
        super().__init__(parent)

        self.setWindowTitle("Factura")
        self.resize(720, 520)

        self.clientes = clientes or []
        self.productos = productos or []
        self.detalles = []

        self.cliente_combo = QComboBox()
        for cliente in self.clientes:
            self.cliente_combo.addItem(cliente["cliente"], cliente["id_cliente"])

        self.tipo_comprobante_input = QComboBox()
        self.tipo_comprobante_input.addItems(["Factura C", "Factura B", "Factura A"])

        self.punto_venta_input = QSpinBox()
        self.punto_venta_input.setMinimum(1)
        self.punto_venta_input.setMaximum(99999)
        self.punto_venta_input.setValue(1)

        self.numero_input = QSpinBox()
        self.numero_input.setMinimum(0)
        self.numero_input.setMaximum(999999999)

        self.fecha_input = QDateEdit()
        self.fecha_input.setCalendarPopup(True)
        self.fecha_input.setDate(QDate.currentDate())

        self.forma_pago_input = QComboBox()
        self.forma_pago_input.addItems(["Efectivo", "Transferencia", "Tarjeta", "Cuenta corriente", "Otro"])

        self.observaciones_input = QTextEdit()

        self.cae_input = QLineEdit()
        self.vencimiento_cae_input = QLineEdit()

        self.estado_arca_input = QComboBox()
        self.estado_arca_input.addItems(["Pendiente", "Preparada", "Autorizada", "Rechazada"])

        self.producto_combo = QComboBox()
        for producto in self.productos:
            self.producto_combo.addItem(producto["descripcion"], producto)

        self.descripcion_input = QLineEdit()

        self.cantidad_input = QDoubleSpinBox()
        self.cantidad_input.setMinimum(0.01)
        self.cantidad_input.setMaximum(999999)
        self.cantidad_input.setDecimals(2)
        self.cantidad_input.setValue(1)

        self.precio_unitario_input = QDoubleSpinBox()
        self.precio_unitario_input.setMaximum(999999999)
        self.precio_unitario_input.setDecimals(2)

        self.iva_item_input = QDoubleSpinBox()
        self.iva_item_input.setMaximum(100)
        self.iva_item_input.setDecimals(2)
        self.iva_item_input.setValue(21)

        self.producto_combo.currentIndexChanged.connect(self.cargar_producto)

        self.tabla_detalles = QTableWidget()
        self.tabla_detalles.setColumnCount(6)
        self.tabla_detalles.setHorizontalHeaderLabels([
            "Producto ID", "Descripcion", "Cantidad", "Precio", "IVA %", "Subtotal"
        ])
        self.tabla_detalles.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_detalles.setEditTriggers(QTableWidget.NoEditTriggers)

        self.subtotal_input = QDoubleSpinBox()
        self.subtotal_input.setMaximum(999999999)
        self.subtotal_input.setDecimals(2)
        self.subtotal_input.setReadOnly(True)

        self.iva_total_input = QDoubleSpinBox()
        self.iva_total_input.setMaximum(999999999)
        self.iva_total_input.setDecimals(2)
        self.iva_total_input.setReadOnly(True)

        self.total_input = QDoubleSpinBox()
        self.total_input.setMaximum(999999999)
        self.total_input.setDecimals(2)
        self.total_input.setReadOnly(True)

        self.btn_agregar_item = QPushButton("Agregar item")
        self.btn_quitar_item = QPushButton("Quitar item")
        self.btn_agregar_item.clicked.connect(self.agregar_item)
        self.btn_quitar_item.clicked.connect(self.quitar_item)

        if self.productos:
            self.cargar_producto()

        datos_form = QFormLayout()
        datos_form.addRow("Cliente:", self.cliente_combo)
        datos_form.addRow("Tipo comprobante:", self.tipo_comprobante_input)
        datos_form.addRow("Punto venta:", self.punto_venta_input)
        datos_form.addRow("Numero:", self.numero_input)
        datos_form.addRow("Fecha:", self.fecha_input)
        datos_form.addRow("Forma pago:", self.forma_pago_input)
        datos_form.addRow("Observaciones:", self.observaciones_input)
        datos_form.addRow("CAE:", self.cae_input)
        datos_form.addRow("Vencimiento CAE:", self.vencimiento_cae_input)
        datos_form.addRow("Estado ARCA:", self.estado_arca_input)

        item_form = QFormLayout()
        item_form.addRow("Producto/servicio:", self.producto_combo)
        item_form.addRow("Descripcion:", self.descripcion_input)
        item_form.addRow("Cantidad:", self.cantidad_input)
        item_form.addRow("Precio unitario:", self.precio_unitario_input)
        item_form.addRow("IVA %:", self.iva_item_input)

        item_botones = QHBoxLayout()
        item_botones.addWidget(self.btn_agregar_item)
        item_botones.addWidget(self.btn_quitar_item)
        item_botones.addStretch()

        totales_form = QFormLayout()
        totales_form.addRow("Subtotal:", self.subtotal_input)
        totales_form.addRow("IVA:", self.iva_total_input)
        totales_form.addRow("Total:", self.total_input)

        botones = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.validar_y_aceptar)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(datos_form)
        layout.addLayout(item_form)
        layout.addLayout(item_botones)
        layout.addWidget(self.tabla_detalles)
        layout.addLayout(totales_form)
        layout.addWidget(botones)

        self.setLayout(layout)

    def cargar_producto(self):
        producto = self.producto_combo.currentData()

        if not producto:
            return

        self.descripcion_input.setText(producto["descripcion"] or "")
        self.precio_unitario_input.setValue(float(producto["precio"] or 0))
        self.iva_item_input.setValue(float(producto["iva"] or 21))

    def agregar_item(self):
        descripcion = self.descripcion_input.text().strip()

        if not descripcion:
            QMessageBox.warning(self, "Datos incompletos", "La descripcion del item es obligatoria.")
            return

        producto = self.producto_combo.currentData()
        producto_id = producto["id_producto"] if producto else None

        cantidad = self.cantidad_input.value()
        precio = self.precio_unitario_input.value()
        iva = self.iva_item_input.value()
        subtotal = cantidad * precio

        detalle = {
            "producto_id": producto_id,
            "descripcion": descripcion,
            "cantidad": cantidad,
            "precio_unitario": precio,
            "iva": iva,
            "subtotal": subtotal,
        }

        self.detalles.append(detalle)
        self.cargar_tabla_detalles()
        self.actualizar_totales()

    def quitar_item(self):
        fila = self.tabla_detalles.currentRow()

        if fila < 0:
            QMessageBox.warning(self, "Seleccion requerida", "Selecciona un item.")
            return

        self.detalles.pop(fila)
        self.cargar_tabla_detalles()
        self.actualizar_totales()

    def cargar_tabla_detalles(self):
        self.tabla_detalles.setRowCount(len(self.detalles))

        for fila, detalle in enumerate(self.detalles):
            valores = [
                detalle["producto_id"] or "",
                detalle["descripcion"],
                detalle["cantidad"],
                detalle["precio_unitario"],
                detalle["iva"],
                detalle["subtotal"],
            ]

            for columna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla_detalles.setItem(fila, columna, item)

        self.tabla_detalles.resizeColumnsToContents()

    def actualizar_totales(self):
        subtotal = sum(item["subtotal"] for item in self.detalles)
        iva_total = sum(item["subtotal"] * item["iva"] / 100 for item in self.detalles)
        total = subtotal + iva_total

        self.subtotal_input.setValue(subtotal)
        self.iva_total_input.setValue(iva_total)
        self.total_input.setValue(total)

    def validar_y_aceptar(self):
        if self.cliente_combo.currentData() is None:
            QMessageBox.warning(self, "Datos incompletos", "Selecciona un cliente.")
            return

        if not self.detalles:
            QMessageBox.warning(self, "Datos incompletos", "Agrega al menos un item.")
            return

        self.accept()

    def datos_factura(self):
        numero = self.numero_input.value()
        if numero == 0:
            numero = None

        return {
            "tipo_comprobante": self.tipo_comprobante_input.currentText(),
            "punto_venta": self.punto_venta_input.value(),
            "numero": numero,
            "fecha": self.fecha_input.date().toString("yyyy-MM-dd"),
            "cliente_id": self.cliente_combo.currentData(),
            "subtotal": self.subtotal_input.value(),
            "iva": self.iva_total_input.value(),
            "total": self.total_input.value(),
            "forma_pago": self.forma_pago_input.currentText(),
            "observaciones": self.observaciones_input.toPlainText().strip(),
            "cae": self.cae_input.text().strip(),
            "vencimiento_cae": self.vencimiento_cae_input.text().strip(),
            "estado_arca": self.estado_arca_input.currentText(),
        }


class FacturasView(QWidget):
    def __init__(self):
        super().__init__()

        self.module = FacturasModule()
        self.facturas_cache = []

        self.tabla = QTableWidget()
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)

        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)

        self.tabla.setColumnCount(11)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Cliente", "Tipo", "PV", "Numero", "Fecha",
            "Subtotal", "IVA", "Total", "Forma pago", "Estado ARCA"
        ])
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)

        self.btn_nueva = QPushButton("Nueva")
        self.btn_ver_detalle = QPushButton("Ver detalle")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_autorizar = QPushButton("🔐 Autorizar en ARCA")
        self.btn_pdf = QPushButton("📄 Generar PDF")

        self.btn_nueva.clicked.connect(self.nueva_factura)
        self.btn_ver_detalle.clicked.connect(self.ver_detalle)
        self.btn_eliminar.clicked.connect(self.eliminar_factura)
        self.btn_actualizar.clicked.connect(self.cargar_facturas)
        self.btn_autorizar.clicked.connect(self.autorizar_en_arca)
        self.btn_pdf.clicked.connect(self.generar_pdf)

        botones_layout = QHBoxLayout()
        botones_layout.addWidget(self.btn_nueva)
        botones_layout.addWidget(self.btn_ver_detalle)
        botones_layout.addWidget(self.btn_eliminar)
        botones_layout.addWidget(self.btn_autorizar)
        botones_layout.addWidget(self.btn_pdf)
        botones_layout.addStretch()
        botones_layout.addWidget(self.btn_actualizar)

        self.lbl_estado = QLabel("")

        layout = QVBoxLayout()
        layout.addLayout(botones_layout)
        layout.addWidget(self.lbl_estado)
        layout.addWidget(self.tabla)

        self.setLayout(layout)
        self.cargar_facturas()

    def cargar_facturas(self):
        self.facturas_cache = self.module.listar()
        self.tabla.setRowCount(len(self.facturas_cache))

        for fila, factura in enumerate(self.facturas_cache):
            valores = [
                factura["id_factura"],
                factura["cliente"],
                factura["tipo_comprobante"],
                factura["punto_venta"],
                factura["numero"] or "",
                factura["fecha"],
                factura["subtotal"],
                factura["iva"],
                factura["total"],
                factura["forma_pago"] or "",
                factura["estado_arca"] or "",
            ]

            for columna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(fila, columna, item)

        self.tabla.resizeColumnsToContents()

    def factura_seleccionada(self):
        fila = self.tabla.currentRow()

        if fila < 0:
            QMessageBox.warning(self, "Seleccion requerida", "Selecciona una factura.")
            return None

        return self.facturas_cache[fila]

    def nueva_factura(self):
        clientes = self.module.listar_clientes()
        productos = self.module.listar_productos()

        if not clientes:
            QMessageBox.warning(self, "Sin clientes", "Primero carga un cliente.")
            return

        dialog = FacturaDialog(self, clientes=clientes, productos=productos)

        if dialog.exec() == QDialog.Accepted:
            self.module.crear(dialog.datos_factura(), dialog.detalles)
            self.cargar_facturas()

    def ver_detalle(self):
        factura = self.factura_seleccionada()

        if factura is None:
            return

        detalles = self.module.obtener_detalles(factura["id_factura"])

        texto = ""
        for detalle in detalles:
            texto += (
                f"{detalle['descripcion']} | "
                f"Cant: {detalle['cantidad']} | "
                f"Precio: {detalle['precio_unitario']} | "
                f"IVA: {detalle['iva']}% | "
                f"Subtotal: {detalle['subtotal']}\n"
            )

        if not texto:
            texto = "Esta factura no tiene detalle."

        QMessageBox.information(self, "Detalle factura", texto)

    def eliminar_factura(self):
        factura = self.factura_seleccionada()

        if factura is None:
            return

        respuesta = QMessageBox.question(
            self,
            "Eliminar factura",
            "Seguro que queres eliminar esta factura?"
        )

        if respuesta == QMessageBox.Yes:
            self.module.eliminar(factura["id_factura"])
            self.cargar_facturas()

    def autorizar_en_arca(self):
        factura = self.factura_seleccionada()
        if factura is None:
            return

        estado = factura["estado_arca"] or ""
        if estado == "Autorizada":
            QMessageBox.information(self, "Ya autorizada", "Esta factura ya fue autorizada en ARCA.")
            return

        respuesta = QMessageBox.question(
            self,
            "Autorizar en ARCA",
            f"¿Autorizar la factura seleccionada en ARCA?\n\nEsto enviará los datos a AFIP.",
        )
        if respuesta != QMessageBox.Yes:
            return

        self.lbl_estado.setText("⏳ Conectando con ARCA...")
        self.btn_autorizar.setEnabled(False)

        self._worker = _ArcaWorker(self.module, factura["id_factura"])
        self._worker.terminado.connect(self._on_arca_ok)
        self._worker.error.connect(self._on_arca_error)
        self._worker.start()

    def _on_arca_ok(self, resultado: dict):
        self.btn_autorizar.setEnabled(True)
        self.lbl_estado.setText(f"✅ Autorizada — CAE: {resultado['cae']}")
        self.cargar_facturas()
        QMessageBox.information(
            self,
            "Factura autorizada",
            f"CAE: {resultado['cae']}\n"
            f"Vencimiento: {resultado['cae_vto']}\n"
            f"Número: {resultado['numero']}\n\n"
            f"PDF generado en:\n{resultado['pdf_path']}",
        )

    def _on_arca_error(self, mensaje: str):
        self.btn_autorizar.setEnabled(True)
        self.lbl_estado.setText("❌ Error al autorizar")
        QMessageBox.critical(self, "Error ARCA", mensaje)

    def generar_pdf(self):
        """Genera PDF de una factura ya autorizada (con CAE)."""
        factura = self.factura_seleccionada()
        if factura is None:
            return

        if not factura["cae"]:
            QMessageBox.warning(
                self,
                "Sin CAE",
                "Esta factura no tiene CAE. Primero autorizala en ARCA.",
            )
            return

        try:
            from app.db import Database
            from app.reports.factura_pdf import generar_pdf as _gen_pdf

            db = Database()
            detalles = db.get_factura_detalles(factura["id_factura"])
            cliente  = db.get_cliente(factura["cliente_id"])
            emisor   = db.get_emisor()
            db.cerrar()

            pdf_path = _gen_pdf(
                factura  = factura,
                cliente  = cliente,
                emisor   = emisor,
                detalles = [dict(d) for d in detalles],
            )

            QMessageBox.information(self, "PDF generado", f"PDF guardado en:\n{pdf_path}")

            # Abrir el PDF automáticamente según el SO
            if sys.platform.startswith("win"):
                os.startfile(pdf_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", pdf_path])
            else:
                subprocess.Popen(["xdg-open", pdf_path])

        except Exception as e:
            QMessageBox.critical(self, "Error al generar PDF", str(e))


class _ArcaWorker(QThread):
    """Hilo para llamar a ARCA sin bloquear la UI."""
    terminado = Signal(dict)
    error     = Signal(str)

    def __init__(self, module, id_factura: int):
        super().__init__()
        self.module      = module
        self.id_factura  = id_factura

    def run(self):
        try:
            resultado = self.module.autorizar_en_arca(self.id_factura)
            self.terminado.emit(resultado)
        except Exception as e:
            self.error.emit(str(e))
