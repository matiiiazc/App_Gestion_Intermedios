from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QLineEdit, QFormLayout, QDialog,
    QDialogButtonBox, QComboBox, QLabel, QGroupBox
)
from PySide6.QtCore import Qt

from app.modules.clientes import ClientesModule


class TrabajosClienteDialog(QDialog):
    def __init__(self, parent=None, cliente_nombre="", trabajos=None):
        super().__init__(parent)
        self.setWindowTitle(f"Trabajos de {cliente_nombre}")
        self.resize(850, 420)

        self.tabla = QTableWidget()
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Tipo", "Descripcion", "Costo", "Final", "Sena",
            "Fecha entrega", "Estado"
        ])
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)

        trabajos = trabajos or []
        self.tabla.setRowCount(len(trabajos))

        for fila, trabajo in enumerate(trabajos):
            valores = [
                trabajo["id_pedido"], trabajo["tipo_trabajo"],
                trabajo["descripcion"] or "", trabajo["precio_costo"],
                trabajo["precio_final"], trabajo["sena"],
                trabajo["fecha"], trabajo["estado"],
            ]
            for columna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(fila, columna, item)

        self.tabla.resizeColumnsToContents()

        botones = QDialogButtonBox(QDialogButtonBox.Close)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.tabla)
        layout.addWidget(botones)
        self.setLayout(layout)


class ClienteDialog(QDialog):
    def __init__(self, parent=None, cliente=None, tipo_inicial="Particular"):
        super().__init__(parent)
        self.setWindowTitle("Cliente")
        self.resize(470, 520)

        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Particular", "Empresa"])

        self.nombre_input = QLineEdit()
        self.apellido_input = QLineEdit()
        self.nombre_empresa_input = QLineEdit()
        self.telefono_input = QLineEdit()
        self.direccion_input = QLineEdit()
        self.localidad_input = QLineEdit()
        self.provincia_input = QLineEdit()
        self.email_input = QLineEdit()
        self.cuil_input = QLineEdit()
        self.dni_input = QLineEdit()

        self.condicion_iva_input = QComboBox()
        self.condicion_iva_input.addItems([
            "", "Consumidor Final", "Monotributo",
            "Responsable Inscripto", "Exento"
        ])

        if cliente:
            tipo = cliente["tipo_cliente"] or "Particular"
            self.tipo_combo.setCurrentText(tipo)
            self.nombre_input.setText(cliente["nombre"] or "")
            self.apellido_input.setText(cliente["apellido"] or "")
            self.nombre_empresa_input.setText(cliente["nombre_empresa"] or "")
            self.telefono_input.setText(cliente["telefono"] or "")
            self.direccion_input.setText(cliente["direccion"] or "")
            self.localidad_input.setText(cliente["localidad"] or "")
            self.provincia_input.setText(cliente["provincia"] or "")
            self.email_input.setText(cliente["email"] or "")
            self.cuil_input.setText(cliente["cuil"] or "")
            self.dni_input.setText(cliente["dni"] or "")
            index_iva = self.condicion_iva_input.findText(cliente["condicion_iva"] or "")
            if index_iva >= 0:
                self.condicion_iva_input.setCurrentIndex(index_iva)
        else:
            self.tipo_combo.setCurrentText(tipo_inicial)

        datos_box = QGroupBox("Datos principales")
        self.datos_form = QFormLayout()
        self.datos_form.addRow("Tipo:", self.tipo_combo)
        self.datos_form.addRow("Nombre:", self.nombre_input)
        self.datos_form.addRow("Apellido:", self.apellido_input)
        self.datos_form.addRow("Empresa:", self.nombre_empresa_input)
        self.datos_form.addRow("Telefono:", self.telefono_input)
        datos_box.setLayout(self.datos_form)

        fiscales_box = QGroupBox("Datos para facturacion")
        self.fiscales_form = QFormLayout()
        self.fiscales_form.addRow("CUIL/CUIT:", self.cuil_input)
        self.fiscales_form.addRow("DNI:", self.dni_input)
        self.fiscales_form.addRow("Condicion IVA:", self.condicion_iva_input)
        self.fiscales_form.addRow("Direccion:", self.direccion_input)
        self.fiscales_form.addRow("Localidad:", self.localidad_input)
        self.fiscales_form.addRow("Provincia:", self.provincia_input)
        self.fiscales_form.addRow("Email:", self.email_input)
        fiscales_box.setLayout(self.fiscales_form)

        botones = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(datos_box)
        layout.addWidget(fiscales_box)
        layout.addWidget(botones)
        self.setLayout(layout)

        self.tipo_combo.currentTextChanged.connect(self.actualizar_campos)
        self.actualizar_campos(self.tipo_combo.currentText())

    def actualizar_campos(self, tipo):
        es_empresa = tipo == "Empresa"
        self.nombre_input.setVisible(not es_empresa)
        self.apellido_input.setVisible(not es_empresa)
        self.nombre_empresa_input.setVisible(es_empresa)
        self.dni_input.setVisible(not es_empresa)
        self.datos_form.labelForField(self.nombre_input).setVisible(not es_empresa)
        self.datos_form.labelForField(self.apellido_input).setVisible(not es_empresa)
        self.datos_form.labelForField(self.nombre_empresa_input).setVisible(es_empresa)
        self.fiscales_form.labelForField(self.dni_input).setVisible(not es_empresa)

    def datos(self):
        return {
            "tipo_cliente": self.tipo_combo.currentText(),
            "nombre": self.nombre_input.text().strip(),
            "apellido": self.apellido_input.text().strip(),
            "nombre_empresa": self.nombre_empresa_input.text().strip(),
            "telefono": self.telefono_input.text().strip(),
            "direccion": self.direccion_input.text().strip(),
            "localidad": self.localidad_input.text().strip(),
            "provincia": self.provincia_input.text().strip(),
            "email": self.email_input.text().strip(),
            "cuil": self.cuil_input.text().strip(),
            "dni": self.dni_input.text().strip(),
            "condicion_iva": self.condicion_iva_input.currentText(),
        }


class ClientesView(QWidget):
    def __init__(self):
        super().__init__()

        self.module = ClientesModule()
        self.clientes_cache = []

        # Filtro tipo
        self.filtro_tipo = QComboBox()
        self.filtro_tipo.addItems(["Todos", "Particular", "Empresa"])
        self.filtro_tipo.currentTextChanged.connect(self.cargar_clientes)

        # Buscador
        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar por nombre, teléfono, CUIL, email...")
        self.buscador.textChanged.connect(self.filtrar_tabla)
        self.buscador.setMinimumWidth(280)

        self.tabla = QTableWidget()
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setColumnCount(10)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Tipo", "Cliente", "Telefono", "CUIL/CUIT",
            "DNI", "Condicion IVA", "Localidad", "Provincia", "Email"
        ])
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.cellDoubleClicked.connect(self.abrir_trabajos_cliente)

        self.btn_nuevo = QPushButton("Nuevo")
        self.btn_editar = QPushButton("Editar")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_actualizar = QPushButton("Actualizar")

        self.btn_nuevo.clicked.connect(self.nuevo_cliente)
        self.btn_editar.clicked.connect(self.editar_cliente)
        self.btn_eliminar.clicked.connect(self.eliminar_cliente)
        self.btn_actualizar.clicked.connect(self.cargar_clientes)

        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Tipo:"))
        filtro_layout.addWidget(self.filtro_tipo)
        filtro_layout.addWidget(self.buscador)
        filtro_layout.addStretch()

        botones_layout = QHBoxLayout()
        botones_layout.addWidget(self.btn_nuevo)
        botones_layout.addWidget(self.btn_editar)
        botones_layout.addWidget(self.btn_eliminar)
        botones_layout.addStretch()
        botones_layout.addWidget(self.btn_actualizar)

        layout = QVBoxLayout()
        layout.addLayout(filtro_layout)
        layout.addLayout(botones_layout)
        layout.addWidget(self.tabla)

        self.setLayout(layout)
        self.cargar_clientes()

    def cargar_clientes(self):
        tipo = self.filtro_tipo.currentText()
        self.clientes_cache = self.module.listar(tipo)
        self._poblar_tabla(self.clientes_cache)
        # Reaplicar filtro de texto si hay algo escrito
        if self.buscador.text():
            self.filtrar_tabla(self.buscador.text())

    def _poblar_tabla(self, clientes):
        self.tabla.setRowCount(len(clientes))
        for fila, cliente in enumerate(clientes):
            valores = [
                cliente["id_cliente"], cliente["tipo_cliente"],
                cliente["cliente"], cliente["telefono"] or "",
                cliente["cuil"] or "", cliente["dni"] or "",
                cliente["condicion_iva"] or "", cliente["localidad"] or "",
                cliente["provincia"] or "", cliente["email"] or "",
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

    def cliente_seleccionado_id(self):
        fila = self.tabla.currentRow()
        if fila < 0 or self.tabla.isRowHidden(fila):
            QMessageBox.warning(self, "Seleccion requerida", "Selecciona un cliente.")
            return None
        return int(self.tabla.item(fila, 0).text())

    def nuevo_cliente(self):
        tipo_actual = self.filtro_tipo.currentText()
        tipo_inicial = tipo_actual if tipo_actual != "Todos" else "Particular"
        dialog = ClienteDialog(self, tipo_inicial=tipo_inicial)

        if dialog.exec() == QDialog.Accepted:
            datos = dialog.datos()
            if datos["tipo_cliente"] == "Particular":
                if not datos["nombre"] or not datos["apellido"]:
                    QMessageBox.warning(self, "Datos incompletos", "Nombre y apellido son obligatorios.")
                    return
                self.module.crear_particular(
                    datos["nombre"], datos["apellido"], datos["telefono"],
                    datos["cuil"], datos["dni"], datos["condicion_iva"],
                    datos["direccion"], datos["localidad"], datos["provincia"], datos["email"]
                )
            else:
                if not datos["nombre_empresa"]:
                    QMessageBox.warning(self, "Datos incompletos", "El nombre de la empresa es obligatorio.")
                    return
                self.module.crear_empresa(
                    datos["nombre_empresa"], datos["telefono"], datos["direccion"],
                    datos["cuil"], datos["condicion_iva"], datos["localidad"],
                    datos["provincia"], datos["email"]
                )
            self.cargar_clientes()

    def editar_cliente(self):
        id_cliente = self.cliente_seleccionado_id()
        if id_cliente is None:
            return
        cliente = self.module.obtener(id_cliente)
        dialog = ClienteDialog(self, cliente)

        if dialog.exec() == QDialog.Accepted:
            datos = dialog.datos()
            if datos["tipo_cliente"] == "Particular":
                if not datos["nombre"] or not datos["apellido"]:
                    QMessageBox.warning(self, "Datos incompletos", "Nombre y apellido son obligatorios.")
                    return
                self.module.editar_particular(
                    id_cliente, datos["nombre"], datos["apellido"],
                    datos["telefono"], datos["cuil"], datos["dni"],
                    datos["condicion_iva"], datos["direccion"],
                    datos["localidad"], datos["provincia"], datos["email"]
                )
            else:
                if not datos["nombre_empresa"]:
                    QMessageBox.warning(self, "Datos incompletos", "El nombre de la empresa es obligatorio.")
                    return
                self.module.editar_empresa(
                    id_cliente, datos["nombre_empresa"], datos["telefono"],
                    datos["direccion"], datos["cuil"], datos["condicion_iva"],
                    datos["localidad"], datos["provincia"], datos["email"]
                )
            self.cargar_clientes()

    def eliminar_cliente(self):
        id_cliente = self.cliente_seleccionado_id()
        if id_cliente is None:
            return
        respuesta = QMessageBox.question(self, "Eliminar cliente", "Seguro que queres eliminar este cliente?")
        if respuesta == QMessageBox.Yes:
            self.module.eliminar(id_cliente)
            self.cargar_clientes()

    def abrir_trabajos_cliente(self, fila, columna):
        id_cliente = int(self.tabla.item(fila, 0).text())
        cliente_nombre = self.tabla.item(fila, 2).text()
        trabajos = self.module.trabajos_cliente(id_cliente)
        dialog = TrabajosClienteDialog(self, cliente_nombre=cliente_nombre, trabajos=trabajos)
        dialog.exec()