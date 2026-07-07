from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QScrollArea,
    QPushButton, QMessageBox, QLineEdit, QFormLayout, QDialog,
    QDialogButtonBox, QComboBox, QTextEdit, QDoubleSpinBox, QDateEdit,
    QGroupBox, QLabel
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

from app.modules.pedidos import PedidosModule


class PedidoDialog(QDialog):
    def __init__(self, parent=None, clientes=None, pedido=None):
        super().__init__(parent)
        self.setWindowTitle("Pedido")
        self.resize(600, 480)

        self.clientes = clientes or []
        self.pedido = pedido

        self.cliente_combo = QComboBox()
        for cliente in self.clientes:
            self.cliente_combo.addItem(cliente["cliente"], cliente["id_cliente"])

        self.fecha_ingreso_input = QDateEdit()
        self.fecha_ingreso_input.setCalendarPopup(True)
        self.fecha_ingreso_input.setDate(QDate.currentDate())

        self.fecha_input = QDateEdit()
        self.fecha_input.setCalendarPopup(True)
        self.fecha_input.setDate(QDate.currentDate())

        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["Pendiente", "En proceso", "Terminado", "Entregado", "Cancelado"])

        self.tipo_trabajo_input = QLineEdit()
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setMaximumHeight(70)

        self.precio_costo_input = QDoubleSpinBox()
        self.precio_costo_input.setMaximum(999999999)
        self.precio_costo_input.setDecimals(2)

        self.precio_final_input = QDoubleSpinBox()
        self.precio_final_input.setMaximum(999999999)
        self.precio_final_input.setDecimals(2)

        self.sena_input = QDoubleSpinBox()
        self.sena_input.setMaximum(999999999)
        self.sena_input.setDecimals(2)

        if pedido:
            index_cliente = self.cliente_combo.findData(pedido["id_cliente"])
            if index_cliente >= 0:
                self.cliente_combo.setCurrentIndex(index_cliente)
            fecha = QDate.fromString(pedido["fecha"], "yyyy-MM-dd")
            if fecha.isValid():
                self.fecha_input.setDate(fecha)
            fecha_ingreso = QDate.fromString(pedido["fecha_ingreso"] or "", "yyyy-MM-dd")
            if fecha_ingreso.isValid():
                self.fecha_ingreso_input.setDate(fecha_ingreso)
            index_estado = self.estado_combo.findText(pedido["estado"] or "Pendiente")
            if index_estado >= 0:
                self.estado_combo.setCurrentIndex(index_estado)
            self.tipo_trabajo_input.setText(pedido["tipo_trabajo"] or "")
            self.descripcion_input.setPlainText(pedido["descripcion"] or "")
            self.precio_costo_input.setValue(float(pedido["precio_costo"] or 0))
            self.precio_final_input.setValue(float(pedido["precio_final"] or 0))
            self.sena_input.setValue(float(pedido["sena"] or 0))

        datos_form = QFormLayout()
        datos_form.addRow("Cliente:", self.cliente_combo)
        datos_form.addRow("Fecha de ingreso:", self.fecha_ingreso_input)
        datos_form.addRow("Fecha de entrega:", self.fecha_input)
        datos_form.addRow("Estado:", self.estado_combo)

        trabajo_form = QFormLayout()
        trabajo_form.addRow("Tipo trabajo:", self.tipo_trabajo_input)
        trabajo_form.addRow("Descripcion:", self.descripcion_input)

        # Costo, Final y Sena en una sola fila, 3 columnas
        precios_layout = QHBoxLayout()

        col_costo = QVBoxLayout()
        col_costo.addWidget(QLabel("Precio costo:"))
        col_costo.addWidget(self.precio_costo_input)

        col_final = QVBoxLayout()
        col_final.addWidget(QLabel("Precio final:"))
        col_final.addWidget(self.precio_final_input)

        col_sena = QVBoxLayout()
        col_sena.addWidget(QLabel("Sena:"))
        col_sena.addWidget(self.sena_input)

        precios_layout.addLayout(col_costo)
        precios_layout.addLayout(col_final)
        precios_layout.addLayout(col_sena)

        trabajo_form.addRow(precios_layout)

        trabajo_box = QGroupBox("Trabajo")
        trabajo_box.setLayout(trabajo_form)

        botones = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.validar_y_aceptar)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(datos_form)
        layout.addWidget(trabajo_box)
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

    def validar_y_aceptar(self):
        if not self.tipo_trabajo_input.text().strip():
            QMessageBox.warning(self, "Datos incompletos", "El tipo de trabajo es obligatorio.")
            return
        self.accept()

    def datos_edicion(self):
        return {
            "id_cliente": self.cliente_combo.currentData(),
            "tipo_trabajo": self.tipo_trabajo_input.text().strip(),
            "descripcion": self.descripcion_input.toPlainText().strip(),
            "precio_costo": self.precio_costo_input.value(),
            "precio_final": self.precio_final_input.value(),
            "sena": self.sena_input.value(),
            "fecha": self.fecha_input.date().toString("yyyy-MM-dd"),
            "fecha_ingreso": self.fecha_ingreso_input.date().toString("yyyy-MM-dd"),
            "estado": self.estado_combo.currentText(),
        }

    def datos_creacion(self):
        trabajo = {
            "tipo_trabajo": self.tipo_trabajo_input.text().strip(),
            "descripcion": self.descripcion_input.toPlainText().strip(),
            "precio_costo": self.precio_costo_input.value(),
            "precio_final": self.precio_final_input.value(),
            "sena": self.sena_input.value(),
        }
        return {
            "id_cliente": self.cliente_combo.currentData(),
            "fecha": self.fecha_input.date().toString("yyyy-MM-dd"),
            "fecha_ingreso": self.fecha_ingreso_input.date().toString("yyyy-MM-dd"),
            "estado": self.estado_combo.currentText(),
            "trabajos": [trabajo],
        }


class PedidosView(QWidget):
    def __init__(self):
        super().__init__()

        self.module = PedidosModule()
        self.pedidos_cache = []

        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar por cliente, tipo, descripcion, estado...")
        self.buscador.textChanged.connect(self.filtrar_tabla)
        self.buscador.setMinimumWidth(320)

        self.filtro_estado = QComboBox()
        self.filtro_estado.addItems(["Todos", "Pendiente", "En proceso", "Terminado", "Entregado", "Cancelado"])
        self.filtro_estado.currentTextChanged.connect(self.cargar_pedidos)

        self.tabla = QTableWidget()
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setColumnCount(11)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Cliente", "Tipo", "Descripcion", "Costo",
            "Final", "Sena", "Saldo", "Fecha ingreso", "Fecha de entrega", "Estado"
        ])
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)

        self.btn_nuevo = QPushButton("Nuevo")
        self.btn_editar = QPushButton("Editar")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_actualizar = QPushButton("Actualizar")

        self.btn_nuevo.clicked.connect(self.nuevo_pedido)
        self.btn_editar.clicked.connect(self.editar_pedido)
        self.btn_eliminar.clicked.connect(self.eliminar_pedido)
        self.btn_actualizar.clicked.connect(self.cargar_pedidos)

        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Estado:"))
        filtro_layout.addWidget(self.filtro_estado)
        filtro_layout.addWidget(self.buscador)
        filtro_layout.addStretch()

        botones_layout = QHBoxLayout()
        botones_layout.addWidget(self.btn_nuevo)
        botones_layout.addWidget(self.btn_editar)
        botones_layout.addWidget(self.btn_eliminar)
        botones_layout.addStretch()
        botones_layout.addWidget(self.btn_actualizar)

        
        self.lbl_subtotal = QLabel("$0.00")
        fuente_subtotal = QFont()
        fuente_subtotal.setBold(True)
        fuente_subtotal.setPointSize(13)
        self.lbl_subtotal.setFont(fuente_subtotal)
        self.lbl_subtotal.setStyleSheet("color: #2ecc71;")  # verde
        self.lbl_subtotal.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        subtotal_layout = QHBoxLayout()
        subtotal_layout.addStretch()
        subtotal_layout.addWidget(self.lbl_subtotal)

        layout = QVBoxLayout()
        layout.addLayout(filtro_layout)
        layout.addLayout(botones_layout)
        layout.addWidget(self.tabla)
        layout.addLayout(subtotal_layout)

        self.setLayout(layout)
        self.cargar_pedidos()

    def cargar_pedidos(self):
        self.pedidos_cache = self.module.listar()
        estado_filtro = self.filtro_estado.currentText()

        if estado_filtro != "Todos":
            filtrados = [p for p in self.pedidos_cache if p["estado"] == estado_filtro]
        else:
            filtrados = self.pedidos_cache

        self._poblar_tabla(filtrados)
        self._actualizar_subtotal(filtrados)
        if self.buscador.text():
            self.filtrar_tabla(self.buscador.text())

    def _poblar_tabla(self, pedidos):
        self.tabla.setRowCount(len(pedidos))
        for fila, pedido in enumerate(pedidos):
            valores = [
                pedido["id_pedido"], pedido["cliente"], pedido["tipo_trabajo"],
                pedido["descripcion"] or "", pedido["precio_costo"],
                pedido["precio_final"], pedido["sena"], pedido["saldo"],
                pedido["fecha_ingreso"] or "", pedido["fecha"], pedido["estado"],
            ]
            for columna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(fila, columna, item)
        self.tabla.resizeColumnsToContents()

    def _actualizar_subtotal(self, pedidos):
        total_saldo = sum((p["saldo"] or 0) for p in pedidos)
        self.lbl_subtotal.setText(f"${total_saldo:.2f}")

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

    def pedido_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0 or self.tabla.isRowHidden(fila):
            QMessageBox.warning(self, "Seleccion requerida", "Selecciona un pedido.")
            return None
        id_pedido = int(self.tabla.item(fila, 0).text())
        for p in self.pedidos_cache:
            if p["id_pedido"] == id_pedido:
                return p
        return None

    def nuevo_pedido(self):
        clientes = self.module.listar_clientes()
        if not clientes:
            QMessageBox.warning(self, "Sin clientes", "Primero carga un cliente.")
            return
        dialog = PedidoDialog(self, clientes=clientes)
        if dialog.exec() == QDialog.Accepted:
            datos = dialog.datos_creacion()
            self.module.crear_varios(
                datos["id_cliente"], datos["fecha"], datos["fecha_ingreso"],
                datos["estado"], datos["trabajos"]
            )
            self.cargar_pedidos()

    def editar_pedido(self):
        pedido = self.pedido_seleccionado()
        if pedido is None:
            return
        clientes = self.module.listar_clientes()
        dialog = PedidoDialog(self, clientes=clientes, pedido=pedido)
        if dialog.exec() == QDialog.Accepted:
            datos = dialog.datos_edicion()
            if datos["id_cliente"] != pedido["id_cliente"]:
                respuesta = QMessageBox.question(
                    self, "Cambiar cliente",
                    "Estas por cambiar el cliente de este trabajo. Seguro que queres continuar?"
                )
                if respuesta != QMessageBox.Yes:
                    return
            self.module.editar(
                pedido["id_pedido"], datos["id_cliente"], datos["tipo_trabajo"],
                datos["descripcion"], datos["precio_costo"], datos["precio_final"],
                datos["sena"], datos["fecha"], datos["fecha_ingreso"], datos["estado"]
            )
            self.cargar_pedidos()

    def eliminar_pedido(self):
        pedido = self.pedido_seleccionado()
        if pedido is None:
            return
        respuesta = QMessageBox.question(self, "Eliminar pedido", "Seguro que queres eliminar este pedido?")
        if respuesta == QMessageBox.Yes:
            self.module.eliminar(pedido["id_pedido"])
            self.cargar_pedidos()