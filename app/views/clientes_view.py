from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QLineEdit, QFormLayout, QDialog,
    QDialogButtonBox, QComboBox, QLabel, QGroupBox, QDoubleSpinBox,
    QTabWidget, QFrame, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
import datetime
from app.modules.clientes import ClientesModule

class PagoDialog(QDialog):
    def __init__(self, parent=None, saldo_actual=0.0):
        super().__init__(parent)
        self.setWindowTitle("Registrar pago")
        self.resize(340, 220)

        self.monto_input = QDoubleSpinBox()
        self.monto_input.setRange(0.01, 99_999_999)
        self.monto_input.setDecimals(2)
        self.monto_input.setPrefix("$ ")
        self.monto_input.setValue(saldo_actual if saldo_actual > 0 else 0.0)

        self.fecha_input = QLineEdit()
        self.fecha_input.setText(datetime.date.today().isoformat())
        self.fecha_input.setPlaceholderText("YYYY-MM-DD")

        self.descripcion_input = QLineEdit()
        self.descripcion_input.setPlaceholderText("Opcional")

        form = QFormLayout()
        form.addRow("Monto:", self.monto_input)
        form.addRow("Fecha:", self.fecha_input)
        form.addRow("Descripción:", self.descripcion_input)

        botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(botones)
        self.setLayout(layout)

    def datos(self):
        return {
            "monto":       self.monto_input.value(),
            "fecha":       self.fecha_input.text().strip(),
            "descripcion": self.descripcion_input.text().strip(),
        }


class TrabajosClienteDialog(QDialog):
    def __init__(self, parent=None, cliente_nombre="", trabajos=None,
                 pagos=None, resumen=None, id_cliente=None, module=None):
        super().__init__(parent)
        self.id_cliente     = id_cliente
        self.module         = module
        self.cliente_nombre = cliente_nombre
        self.setWindowTitle(f"Historial — {cliente_nombre}")
        self.resize(900, 560)

        tabs = QTabWidget()
        tabs.addTab(self._tab_trabajos(trabajos or []),  "Trabajos")
        tabs.addTab(self._tab_pagos(pagos or []),        "Pagos adicionales")

        # ── Resumen financiero ──
        resumen = resumen or {}
        resumen_box = QGroupBox("")
        resumen_layout = QHBoxLayout()

        def _stat(label, valor, color=None):
            col = QVBoxLayout()
            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val = QLabel(f"$ {valor:,.2f}")
            val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setPointSize(13)
            font.setBold(True)
            val.setFont(font)
            if color:
                val.setStyleSheet(f"color: {color};")
            col.addWidget(lbl)
            col.addWidget(val)
            return col

        resumen_layout.addLayout(_stat("Total facturado",
                                       resumen.get("total_facturado", 0)))

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        resumen_layout.addWidget(sep1)

        resumen_layout.addLayout(_stat("Señas",
                                       resumen.get("total_senas", 0), "#4a9eff"))
        resumen_layout.addLayout(_stat("Pagos adicionales",
                                       resumen.get("total_pagos_extra", 0), "#4a9eff"))
        resumen_layout.addLayout(_stat("Total pagado",
                                       resumen.get("total_pagado", 0), "#2ecc71"))

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.VLine)
        resumen_layout.addWidget(sep2)

        saldo = resumen.get("saldo", 0)
        color_saldo = "#e74c3c" if saldo > 0 else "#2ecc71"
        resumen_layout.addLayout(_stat("Saldo deudor", saldo, color_saldo))

        resumen_box.setLayout(resumen_layout)

        # ── Botón pago ──
        self.btn_pago = QPushButton("Registrar pago")
        self.btn_pago.setFixedHeight(36)
        self.btn_pago.clicked.connect(self._registrar_pago)

        botones = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        botones.rejected.connect(self.reject)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.btn_pago)
        btn_row.addStretch()
        btn_row.addWidget(botones)

        layout = QVBoxLayout()
        layout.addWidget(resumen_box)
        layout.addWidget(tabs)
        layout.addLayout(btn_row)
        self.setLayout(layout)

        self._tabs            = tabs
        self._resumen_box     = resumen_box
        self._resumen_layout  = resumen_layout

    # ── Tabs ──────────────────────────────────────────────────────────────

    def _tab_trabajos(self, trabajos):
        widget = QWidget()
        tabla  = QTableWidget()
        tabla.setAlternatingRowColors(True)
        tabla.verticalHeader().setVisible(False)
        tabla.setColumnCount(8)
        tabla.setHorizontalHeaderLabels([
            "ID", "Tipo", "Descripción", "Costo", "Final",
            "Seña", "Fecha entrega", "Estado"
        ])
        tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tabla.setRowCount(len(trabajos))

        for fila, t in enumerate(trabajos):
            valores = [
                t["id_pedido"], t["tipo_trabajo"], t["descripcion"] or "",
                t["precio_costo"], t["precio_final"], t["sena"],
                t["fecha"], t["estado"],
            ]
            for col, val in enumerate(valores):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                tabla.setItem(fila, col, item)
        tabla.resizeColumnsToContents()

        lay = QVBoxLayout()
        lay.addWidget(tabla)
        widget.setLayout(lay)
        return widget

    def _tab_pagos(self, pagos):
        self._tabla_pagos = QTableWidget()
        self._tabla_pagos.setAlternatingRowColors(True)
        self._tabla_pagos.verticalHeader().setVisible(False)
        self._tabla_pagos.setColumnCount(4)
        self._tabla_pagos.setHorizontalHeaderLabels(
            ["ID", "Monto", "Fecha", "Descripción"]
        )
        self._tabla_pagos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._tabla_pagos.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._cargar_tabla_pagos(pagos)

        self.btn_eliminar_pago = QPushButton("Eliminar pago seleccionado")
        self.btn_eliminar_pago.clicked.connect(self._eliminar_pago)

        widget = QWidget()
        lay    = QVBoxLayout()
        lay.addWidget(self._tabla_pagos)
        lay.addWidget(self.btn_eliminar_pago)
        widget.setLayout(lay)
        return widget

    def _cargar_tabla_pagos(self, pagos):
        self._tabla_pagos.setRowCount(len(pagos))
        for fila, p in enumerate(pagos):
            for col, val in enumerate([
                p["id_pago"], f"$ {p['monto']:,.2f}", p["fecha"],
                p["descripcion"] or ""
            ]):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self._tabla_pagos.setItem(fila, col, item)
        self._tabla_pagos.resizeColumnsToContents()

    # ── Acciones ──────────────────────────────────────────────────────────

    def _registrar_pago(self):
        if not self.module or self.id_cliente is None:
            return
        resumen = self.module.resumen_financiero(self.id_cliente)
        dialog  = PagoDialog(self, saldo_actual=resumen["saldo"])
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        d = dialog.datos()
        if d["monto"] <= 0:
            QMessageBox.warning(self, "Monto inválido", "El monto debe ser mayor a 0.")
            return
        self.module.registrar_pago(
            self.id_cliente, d["monto"], d["fecha"], d["descripcion"]
        )
        self._refrescar()

    def _eliminar_pago(self):
        fila = self._tabla_pagos.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Selección requerida",
                                "Seleccioná un pago para eliminar.")
            return
        id_pago = int(self._tabla_pagos.item(fila, 0).text())
        resp = QMessageBox.question(self, "Eliminar pago",
                                    "¿Seguro que querés eliminar este pago?")
        if resp == QMessageBox.StandardButton.Yes:
            self.module.eliminar_pago(id_pago)
            self._refrescar()

    def _refrescar(self):
        pagos   = self.module.pagos_cliente(self.id_cliente)
        resumen = self.module.resumen_financiero(self.id_cliente)
        self._cargar_tabla_pagos(pagos)

        valores = [
            resumen["total_facturado"],
            resumen["total_senas"],
            resumen["total_pagos_extra"],
            resumen["total_pagado"],
            resumen["saldo"],
        ]
        colores = [None, "#4a9eff", "#4a9eff", "#2ecc71",
                   "#e74c3c" if resumen["saldo"] > 0 else "#2ecc71"]

        idx_val = 0
        for i in range(self._resumen_layout.count()):
            item = self._resumen_layout.itemAt(i)
            if item and item.layout():
                col_lay    = item.layout()
                val_widget = col_lay.itemAt(1).widget()
                if val_widget is not None:
                    val_widget.setText(f"$ {valores[idx_val]:,.2f}")
                    c = colores[idx_val]
                    val_widget.setStyleSheet(f"color: {c};" if c else "")
                    idx_val += 1


class ClienteDialog(QDialog):
    def __init__(self, parent=None, cliente=None, tipo_inicial="Particular"):
        super().__init__(parent)
        self.setWindowTitle("Cliente")
        self.resize(420, 340)

        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Particular", "Empresa"])

        self.nombre_input         = QLineEdit()
        self.apellido_input       = QLineEdit()
        self.nombre_empresa_input = QLineEdit()
        self.telefono_input       = QLineEdit()
        self.direccion_input      = QLineEdit()
        self.email_input          = QLineEdit()

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

        datos_box = QGroupBox("Datos del cliente")
        self.form = QFormLayout()
        self.form.addRow("Tipo:", self.tipo_combo)

        self.lbl_nombre   = QLabel("Nombre:")
        self.lbl_apellido = QLabel("Apellido:")
        self.lbl_empresa  = QLabel("Empresa:")
        self.form.addRow(self.lbl_nombre,   self.nombre_input)
        self.form.addRow(self.lbl_apellido, self.apellido_input)
        self.form.addRow(self.lbl_empresa,  self.nombre_empresa_input)
        self.form.addRow("Telefono:",  self.telefono_input)
        self.form.addRow("Direccion:", self.direccion_input)
        self.form.addRow("Email:",     self.email_input)
        datos_box.setLayout(self.form)

        botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
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
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.cellDoubleClicked.connect(self.abrir_trabajos_cliente)

        self.btn_nuevo      = QPushButton("Nuevo")
        self.btn_editar     = QPushButton("Editar")
        self.btn_eliminar   = QPushButton("Eliminar")
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
                c["id_cliente"], c["tipo_cliente"], c["cliente"],
                c["telefono"] or "", c["direccion"] or "",
                c["email"] or "", c["cantidad_trabajos"],
            ]
            for columna, valor in enumerate(valores):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
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

        if dialog.exec() == QDialog.DialogCode.Accepted:
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

        if dialog.exec() == QDialog.DialogCode.Accepted:
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
        if respuesta == QMessageBox.StandardButton.Yes:
            self.module.eliminar(id_cliente)
            self.cargar_clientes()

    def abrir_trabajos_cliente(self, fila, columna):
        id_cliente     = int(self.tabla.item(fila, 0).text())
        cliente_nombre = self.tabla.item(fila, 2).text()
        trabajos       = self.module.trabajos_cliente(id_cliente)
        pagos          = self.module.pagos_cliente(id_cliente)
        resumen        = self.module.resumen_financiero(id_cliente)
        dialog = TrabajosClienteDialog(
            self,
            cliente_nombre=cliente_nombre,
            trabajos=trabajos,
            pagos=pagos,
            resumen=resumen,
            id_cliente=id_cliente,
            module=self.module,
        )
        dialog.exec()