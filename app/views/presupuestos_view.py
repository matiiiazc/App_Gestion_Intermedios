import os
import sys
import subprocess

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QScrollArea,
    QPushButton, QMessageBox, QLineEdit, QFormLayout, QDialog,
    QDialogButtonBox, QComboBox, QDoubleSpinBox, QDateEdit, QLabel, QTextEdit
)
from PySide6.QtCore import Qt, QDate

from app.modules.presupuestos import PresupuestosModule
from app.modules.presupuesto_pdf import generar_pdf_presupuesto
from app.modules.orden_pedido_pdf import get_base_path
from app.widgets import ComboBoxSinScroll


class PresupuestoDialog(QDialog):
    def __init__(self, parent=None, clientes=None, presupuesto=None):
        super().__init__(parent)
        self.setWindowTitle("Presupuesto")
        self.resize(430, 400)
        self.presupuesto = presupuesto

        self.cliente_combo = ComboBoxSinScroll()
        self.clientes = clientes or []
        for cliente in self.clientes:
            self.cliente_combo.addItem(cliente["cliente"], cliente["id_cliente"])

        self.tipo_trabajo_input = QLineEdit()
        self.descripcion_input = QTextEdit()

        self.fecha_ingreso_input = QDateEdit()
        self.fecha_ingreso_input.setCalendarPopup(True)
        self.fecha_ingreso_input.setDate(QDate.currentDate())

        self.fecha_inicio_input = QDateEdit()
        self.fecha_inicio_input.setCalendarPopup(True)
        self.fecha_inicio_input.setDate(QDate.currentDate())

        self.fecha_expiracion_input = QDateEdit()
        self.fecha_expiracion_input.setCalendarPopup(True)
        self.fecha_expiracion_input.setDate(QDate.currentDate().addDays(15))

        self.total_input = QDoubleSpinBox()
        self.total_input.setMaximum(999999999)
        self.total_input.setDecimals(2)

        if presupuesto:
            index_cliente = self.cliente_combo.findData(presupuesto["id_cliente"])
            if index_cliente >= 0:
                self.cliente_combo.setCurrentIndex(index_cliente)
            self.tipo_trabajo_input.setText(presupuesto["tipo_trabajo"] or "")
            self.descripcion_input.setPlainText(presupuesto["descripcion"] or "")
            self.total_input.setValue(float(presupuesto["total"] or 0))
            self.set_fecha(self.fecha_ingreso_input, presupuesto["fecha_ingreso"])
            self.set_fecha(self.fecha_inicio_input, presupuesto["fecha_inicio"])
            self.set_fecha(self.fecha_expiracion_input, presupuesto["fecha_expiracion"])

        form = QFormLayout()
        form.addRow("Cliente:", self.cliente_combo)
        form.addRow("Tipo trabajo:", self.tipo_trabajo_input)
        form.addRow("Descripcion:", self.descripcion_input)
        form.addRow("Fecha ingreso:", self.fecha_ingreso_input)
        form.addRow("Fecha inicio:", self.fecha_inicio_input)
        form.addRow("Fecha expiracion:", self.fecha_expiracion_input)
        form.addRow("Total:", self.total_input)

        botones = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.validar_y_aceptar)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(botones)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        _container = QWidget()
        _container.setLayout(layout)
        scroll.setWidget(_container)
        _outer = QVBoxLayout()
        _outer.setContentsMargins(0, 0, 0, 0)
        _outer.setSpacing(0)
        _outer.addWidget(scroll)
        self.setLayout(_outer)

    def set_fecha(self, widget, valor):
        fecha = QDate.fromString(valor or "", "yyyy-MM-dd")
        if fecha.isValid():
            widget.setDate(fecha)

    def validar_y_aceptar(self):
        if not self.tipo_trabajo_input.text().strip():
            QMessageBox.warning(self, "Datos incompletos", "El tipo de trabajo es obligatorio.")
            return
        self.accept()

    def datos(self):
        return {
            "id_cliente": self.cliente_combo.currentData(),
            "tipo_trabajo": self.tipo_trabajo_input.text().strip(),
            "descripcion": self.descripcion_input.toPlainText().strip(),
            "fecha_ingreso": self.fecha_ingreso_input.date().toString("yyyy-MM-dd"),
            "fecha_inicio": self.fecha_inicio_input.date().toString("yyyy-MM-dd"),
            "fecha_expiracion": self.fecha_expiracion_input.date().toString("yyyy-MM-dd"),
            "total": self.total_input.value(),
        }


class PresupuestosView(QWidget):
    def __init__(self):
        super().__init__()

        self.module = PresupuestosModule()
        self.presupuestos_cache = []

        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar por cliente, tipo de trabajo...")
        self.buscador.textChanged.connect(self.filtrar_tabla)
        self.buscador.setMinimumWidth(280)

        self.filtro_estado = ComboBoxSinScroll()
        self.filtro_estado.addItems(["Todos", "Pendiente", "Aceptado", "Rechazado"])
        self.filtro_estado.currentTextChanged.connect(self.cargar_presupuestos)

        self.tabla = QTableWidget()
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setColumnCount(9)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Cliente", "Tipo", "Descripcion", "Fecha ingreso",
            "Fecha inicio", "Fecha expiracion", "Total", "Estado"
        ])
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)

        self.btn_nuevo = QPushButton("Nuevo")
        self.btn_editar = QPushButton("Editar")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_aceptar = QPushButton("Aceptar presupuesto")
        self.btn_generar_pdf = QPushButton("Generar presupuesto")

        self.btn_nuevo.clicked.connect(self.nuevo_presupuesto)
        self.btn_editar.clicked.connect(self.editar_presupuesto)
        self.btn_eliminar.clicked.connect(self.eliminar_presupuesto)
        self.btn_actualizar.clicked.connect(self.cargar_presupuestos)
        self.btn_aceptar.clicked.connect(self.aceptar_presupuesto)
        self.btn_generar_pdf.clicked.connect(self.generar_presupuesto_pdf)

        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Estado:"))
        filtro_layout.addWidget(self.filtro_estado)
        filtro_layout.addWidget(self.buscador)
        filtro_layout.addStretch()

        botones_layout = QHBoxLayout()
        botones_layout.addWidget(self.btn_nuevo)
        botones_layout.addWidget(self.btn_editar)
        botones_layout.addWidget(self.btn_aceptar)
        botones_layout.addWidget(self.btn_eliminar)
        botones_layout.addWidget(self.btn_generar_pdf)
        botones_layout.addStretch()
        botones_layout.addWidget(self.btn_actualizar)

        layout = QVBoxLayout()
        layout.addLayout(filtro_layout)
        layout.addLayout(botones_layout)
        layout.addWidget(self.tabla)

        self.setLayout(layout)
        self.cargar_presupuestos()

    def cargar_presupuestos(self):
        self.presupuestos_cache = self.module.listar()
        estado_filtro = self.filtro_estado.currentText()

        if estado_filtro != "Todos":
            filtrados = [p for p in self.presupuestos_cache if (p["estado"] if "estado" in p.keys() else "Pendiente") == estado_filtro]
        else:
            filtrados = self.presupuestos_cache

        self._poblar_tabla(filtrados)
        if self.buscador.text():
            self.filtrar_tabla(self.buscador.text())

    def _poblar_tabla(self, presupuestos):
        self.tabla.setRowCount(len(presupuestos))
        for fila, p in enumerate(presupuestos):
            valores = [
                p["id_presupuesto"], p["cliente"], p["tipo_trabajo"], p["descripcion"] or "",
                p["fecha_ingreso"], p["fecha_inicio"] or "",
                p["fecha_expiracion"] or "", p["total"],
                p["estado"] if "estado" in p.keys() else "Pendiente",
            ]
            for columna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(fila, columna, item)
        self.tabla.resizeColumnsToContents()

    def filtrar_tabla(self, texto):
        texto = texto.lower().strip()
        for fila in range(self.tabla.rowCount()):
            mostrar = False
            if not texto:
                mostrar = True
            else:
                for col in range(self.tabla.columnCount()):
                    item = self.tabla.item(fila, col)
                    if item and texto in item.text().lower():
                        mostrar = True
                        break
            self.tabla.setRowHidden(fila, not mostrar)

    def presupuesto_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0 or self.tabla.isRowHidden(fila):
            QMessageBox.warning(self, "Seleccion requerida", "Selecciona un presupuesto.")
            return None
        id_presupuesto = int(self.tabla.item(fila, 0).text())
        for p in self.presupuestos_cache:
            if p["id_presupuesto"] == id_presupuesto:
                return p
        return None

    def nuevo_presupuesto(self):
        clientes = self.module.listar_clientes()
        if not clientes:
            QMessageBox.warning(self, "Sin clientes", "Primero carga un cliente.")
            return
        dialog = PresupuestoDialog(self, clientes=clientes)
        if dialog.exec() == QDialog.Accepted:
            datos = dialog.datos()
            self.module.crear(
                datos["id_cliente"], datos["tipo_trabajo"], datos["descripcion"],
                datos["fecha_ingreso"], datos["fecha_inicio"],
                datos["fecha_expiracion"], datos["total"]
            )
            self.cargar_presupuestos()

    def editar_presupuesto(self):
        presupuesto = self.presupuesto_seleccionado()
        if presupuesto is None:
            return
        clientes = self.module.listar_clientes()
        dialog = PresupuestoDialog(self, clientes=clientes, presupuesto=presupuesto)
        if dialog.exec() == QDialog.Accepted:
            datos = dialog.datos()
            if datos["id_cliente"] != presupuesto["id_cliente"]:
                respuesta = QMessageBox.question(
                    self, "Cambiar cliente",
                    "Estas por cambiar el cliente de este presupuesto. Seguro que queres continuar?"
                )
                if respuesta != QMessageBox.Yes:
                    return
            self.module.editar(
                presupuesto["id_presupuesto"], datos["id_cliente"], datos["tipo_trabajo"],
                datos["descripcion"], datos["fecha_ingreso"], datos["fecha_inicio"],
                datos["fecha_expiracion"], datos["total"]
            )
            self.cargar_presupuestos()

    def eliminar_presupuesto(self):
        presupuesto = self.presupuesto_seleccionado()
        if presupuesto is None:
            return
        respuesta = QMessageBox.question(self, "Eliminar presupuesto", "Seguro que queres eliminar este presupuesto?")
        if respuesta == QMessageBox.Yes:
            self.module.eliminar(presupuesto["id_presupuesto"])
            self.cargar_presupuestos()

    def aceptar_presupuesto(self):
        presupuesto = self.presupuesto_seleccionado()
        if presupuesto is None:
            return
        estado = presupuesto["estado"] if "estado" in presupuesto.keys() else "Pendiente"
        if estado == "Aceptado":
            QMessageBox.information(self, "Presupuesto ya aceptado", "Este presupuesto ya fue aceptado y pasado a pedidos.")
            return
        respuesta = QMessageBox.question(
            self, "Aceptar presupuesto",
            "Seguro que queres aceptar este presupuesto y pasarlo a pedidos?"
        )
        if respuesta == QMessageBox.Yes:
            creado = self.module.aceptar(presupuesto["id_presupuesto"])
            if creado:
                self.cargar_presupuestos()
                QMessageBox.information(self, "Presupuesto aceptado", "El presupuesto se agrego automaticamente a pedidos.")
            else:
                QMessageBox.warning(self, "No se pudo aceptar", "No se pudo aceptar el presupuesto.")

    def generar_presupuesto_pdf(self):
        presupuesto = self.presupuesto_seleccionado()
        if presupuesto is None:
            return

        carpeta = get_base_path() / "Presupuestos generados"
        try:
            carpeta.mkdir(parents=True, exist_ok=True)
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo crear la carpeta 'Presupuestos generados':\n{error}")
            return

        cliente_limpio = "".join(
            c for c in str(presupuesto["cliente"]) if c.isalnum() or c in (" ", "_", "-")
        ).strip().replace(" ", "_")
        nombre_archivo = f"presupuesto_{presupuesto['id_presupuesto']:04d}_{cliente_limpio}.pdf"
        ruta = carpeta / nombre_archivo

        try:
            generar_pdf_presupuesto(presupuesto, ruta)
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo generar el presupuesto:\n{error}")
            return

        respuesta = QMessageBox.question(
            self, "Presupuesto generado",
            f"El presupuesto se guardo en:\n{ruta}\n\nQueres abrirlo ahora?"
        )
        if respuesta == QMessageBox.Yes:
            self._abrir_archivo(str(ruta))

    def _abrir_archivo(self, ruta):
        try:
            if sys.platform.startswith("win"):
                os.startfile(ruta)
            elif sys.platform == "darwin":
                subprocess.run(["open", ruta], check=False)
            else:
                subprocess.run(["xdg-open", ruta], check=False)
        except Exception as error:
            QMessageBox.warning(self, "Aviso", f"No se pudo abrir el archivo automaticamente:\n{error}")