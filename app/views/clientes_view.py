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
            "ID", "Tipo", "Descripcion", "Costo", "Final",
            "Sena", "Fecha entrega", "Estado"
        ])
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)

        trabajos = trabajos or []
        self.tabla.setRowCount(len(trabajos))
        for fila, trabajo in enumerate(trabajos):
            valores = [
                trabajo["id_pedido"],
                trabajo["tipo_trabajo"],
                trabajo["descripcion"] or "",
                trabajo["precio_costo"],
                trabajo["precio_final"],
                trabajo["sena"],
                trabajo["fecha"],
                trabajo["estado"],
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
        self.resize(420, 340)

        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Particular", "Empresa"])

        # Campos Particular
        self.nombre_input       = QLineEdit()
        self.apellido_input     = QLineEdit()
        # Campo Empresa
        self.nombre_empresa_input = QLineEdit()
        # Campos comunes
        self.telefono_input     = QLineEdit()
        self.direccion_input    = QLineEdit()
        self.email_input        = QLineEdit()

        # Precargar si es edición
        if cliente:
            tipo = cliente["tipo_cliente"] or "Particular"
            self.tipo_combo.setCurrentText(tipo)
            self.nombre_input.setText(cliente["nombre"] or "")
            self.apellido_input.setText(cliente["apellido"] or "")
            self.nombre_empresa_input.setText(cliente["nombre_empresa"] or "")
            self.telefono_input.setText(cliente["telefono"] or "")
            self.direccion_input.setText(cliente["direccion"] or "")
            self.email_input.setText(cliente["email"] or "")
        else:
            self.tipo_combo.setCurrentText(tipo_inicial)

        # Layout
        datos_box  = QGroupBox("Datos del cliente")
        self.form  = QFormLayout()
        self.form.addRow("Tipo:", self.tipo_combo)

        self.lbl_nombre   = QLabel("Nombre:")
        self.lbl_apellido = QLabel("Apellido:")
        self.lbl_empresa  = QLabel("Empresa:")
        self.form.addRow(self.lbl_nombre,   self.nombre_input)
        self.form.addRow(self.lbl_apellido, self.apellido_input)
        self.form.addRow(self.lbl_empresa,  self.nombre_empresa_input)
        self.form.addRow("Telefono:",   self.telefono_input)
        self.form.addRow("Direccion:",  self.direccion_input)
        self.form.addRow("Email:",      self.email_input)
        datos_box.setLayout(self.form)

        botones = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(datos_box)
        layout.addWidget(botones)
        self.setLayout(layout)

        self.tipo_combo.currentTextChanged.connect(self._actualizar_campos)
        self._actualizar_campos(self.tipo_combo.currentText())

    def _actualizar_campos(self, tipo):
        es_empresa = tipo == "Empresa"
        self.nombre_input.setVisible(not es_empresa)
        self.apellido_input.setVisible(not es_empresa)
        self.nombre_empresa_input.setVisible(es_empresa)
        self.lbl_nombre.setVisible(not es_empresa)
        self.lbl_apellido.setVisible(not es_empresa)
        self.lbl_empresa.setVisible(es_empresa)

    def datos(self):
        return {
            "tipo_cliente":   self.tipo_combo.currentText(),
            "nombre":         self.nombre_input.text().strip(),
            "apellido":       self.apellido_input.text().strip(),
            "nombre_empresa": self.nombre_empresa_input.text().strip(),
            "telefono":       self.telefono_input.text().strip(),
            "direccion":      self.direccion_input.text().strip(),
            "email":          self.email_input.text().strip(),
        }


class ClientesView(QWidget):
    def __init__(self):
        super().__init__()
        self.module = ClientesModule()

        self.filtro_tipo = QComboBox()
        self.filtro_tipo.addItems(["Todos", "Particular", "Empresa"])
        self.filtro_tipo.currentTextChanged.connect(self.cargar_clientes)

        self.tabla = QTableWidget()
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Tipo", "Nombre / Empresa",
            "Telefono", "Direccion", "Email", "Trabajos"
        ])
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.cellDoubleClicked.connect(self.abrir_trabajos_cliente)

        self.btn_nuevo    = QPushButton("Nuevo")
        self.btn_editar   = QPushButton("Editar")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_actualizar = QPushButton("Actualizar")

        self.btn_nuevo.clicked.connect(self.nuevo_cliente)
        self.btn_editar.clicked.connect(self.editar_cliente)
        self.btn_eliminar.clicked.connect(self.eliminar_cliente)
        self.btn_actualizar.clicked.connect(self.cargar_clientes)

        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Tipo:"))
        filtro_layout.addWidget(self.filtro_tipo)
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
        clientes = self.module.listar(tipo)
        self.tabla.setRowCount(len(clientes))
        for fila, c in enumerate(clientes):
            valores = [
                c["id_cliente"],
                c["tipo_cliente"],
                c["cliente"],
                c["telefono"] or "",
                c["direccion"] or "",
                c["email"] or "",
                c["cantidad_trabajos"],
            ]
            for columna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(fila, columna, item)
        self.tabla.resizeColumnsToContents()

    def _id_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Seleccion requerida", "Selecciona un cliente.")
            return None
        return int(self.tabla.item(fila, 0).text())

    def nuevo_cliente(self):
        tipo_actual  = self.filtro_tipo.currentText()
        tipo_inicial = tipo_actual if tipo_actual != "Todos" else "Particular"
        dialog = ClienteDialog(self, tipo_inicial=tipo_inicial)

        if dialog.exec() == QDialog.Accepted:
            d = dialog.datos()
            if d["tipo_cliente"] == "Particular":
                if not d["nombre"] or not d["apellido"]:
                    QMessageBox.warning(self, "Datos incompletos",
                                        "Nombre y apellido son obligatorios.")
                    return
                self.module.crear_particular(
                    d["nombre"], d["apellido"],
                    d["telefono"], d["direccion"], d["email"]
                )
            else:
                if not d["nombre_empresa"]:
                    QMessageBox.warning(self, "Datos incompletos",
                                        "El nombre de la empresa es obligatorio.")
                    return
                self.module.crear_empresa(
                    d["nombre_empresa"],
                    d["telefono"], d["direccion"], d["email"]
                )
            self.cargar_clientes()

    def editar_cliente(self):
        id_cliente = self._id_seleccionado()
        if id_cliente is None:
            return
        cliente = self.module.obtener(id_cliente)
        dialog  = ClienteDialog(self, cliente)

        if dialog.exec() == QDialog.Accepted:
            d = dialog.datos()
            if d["tipo_cliente"] == "Particular":
                if not d["nombre"] or not d["apellido"]:
                    QMessageBox.warning(self, "Datos incompletos",
                                        "Nombre y apellido son obligatorios.")
                    return
                self.module.editar_particular(
                    id_cliente, d["nombre"], d["apellido"],
                    d["telefono"], d["direccion"], d["email"]
                )
            else:
                if not d["nombre_empresa"]:
                    QMessageBox.warning(self, "Datos incompletos",
                                        "El nombre de la empresa es obligatorio.")
                    return
                self.module.editar_empresa(
                    id_cliente, d["nombre_empresa"],
                    d["telefono"], d["direccion"], d["email"]
                )
            self.cargar_clientes()

    def eliminar_cliente(self):
        id_cliente = self._id_seleccionado()
        if id_cliente is None:
            return
        respuesta = QMessageBox.question(
            self, "Eliminar cliente",
            "Seguro que queres eliminar este cliente?"
        )
        if respuesta == QMessageBox.Yes:
            self.module.eliminar(id_cliente)
            self.cargar_clientes()

    def abrir_trabajos_cliente(self, fila, columna):
        id_cliente     = int(self.tabla.item(fila, 0).text())
        cliente_nombre = self.tabla.item(fila, 2).text()
        trabajos       = self.module.trabajos_cliente(id_cliente)
        dialog = TrabajosClienteDialog(self, cliente_nombre, trabajos)
        dialog.exec()