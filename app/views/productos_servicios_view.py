from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QScrollArea,
    QPushButton, QMessageBox, QLineEdit, QFormLayout, QDialog,
    QDialogButtonBox, QDoubleSpinBox, QComboBox, QLabel
)
from PySide6.QtCore import Qt

from app.modules.productos_servicios import ProductosServiciosModule


class ProductoServicioDialog(QDialog):
    def __init__(self, parent=None, producto=None):
        super().__init__(parent)
        self.setWindowTitle("Producto / Servicio")
        self.resize(420, 330)

        self.codigo_input = QLineEdit()
        self.descripcion_input = QLineEdit()

        self.precio_input = QDoubleSpinBox()
        self.precio_input.setMaximum(999999999)
        self.precio_input.setDecimals(2)

        self.iva_input = QDoubleSpinBox()
        self.iva_input.setMaximum(100)
        self.iva_input.setDecimals(2)
        self.iva_input.setValue(21)

        self.unidad_input = QComboBox()
        self.unidad_input.addItems(["unidad", "hora", "metro", "m2", "kg", "litro", "servicio"])

        self.stock_input = QDoubleSpinBox()
        self.stock_input.setMaximum(999999999)
        self.stock_input.setDecimals(2)

        self.rubro_input = QLineEdit()

        if producto:
            self.codigo_input.setText(producto["codigo"] or "")
            self.descripcion_input.setText(producto["descripcion"] or "")
            self.precio_input.setValue(float(producto["precio"] or 0))
            self.iva_input.setValue(float(producto["iva"] or 21))
            index_unidad = self.unidad_input.findText(producto["unidad"] or "unidad")
            if index_unidad >= 0:
                self.unidad_input.setCurrentIndex(index_unidad)
            self.stock_input.setValue(float(producto["stock"] or 0))
            self.rubro_input.setText(producto["rubro"] or "")

        form = QFormLayout()
        form.addRow("Codigo:", self.codigo_input)
        form.addRow("Descripcion:", self.descripcion_input)
        form.addRow("Precio:", self.precio_input)
        form.addRow("IVA %:", self.iva_input)
        form.addRow("Unidad:", self.unidad_input)
        form.addRow("Stock:", self.stock_input)
        form.addRow("Rubro:", self.rubro_input)

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

    def validar_y_aceptar(self):
        if not self.descripcion_input.text().strip():
            QMessageBox.warning(self, "Datos incompletos", "La descripcion es obligatoria.")
            return
        self.accept()

    def datos(self):
        return {
            "codigo": self.codigo_input.text().strip(),
            "descripcion": self.descripcion_input.text().strip(),
            "precio": self.precio_input.value(),
            "iva": self.iva_input.value(),
            "unidad": self.unidad_input.currentText(),
            "stock": self.stock_input.value(),
            "rubro": self.rubro_input.text().strip(),
        }


class ProductosServiciosView(QWidget):
    def __init__(self):
        super().__init__()

        self.module = ProductosServiciosModule()
        self.productos_cache = []

        self.buscador = QLineEdit()
        self.buscador.setPlaceholderText("Buscar por descripcion, codigo, rubro...")
        self.buscador.textChanged.connect(self.filtrar_tabla)
        self.buscador.setMinimumWidth(280)

        self.tabla = QTableWidget()
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Codigo", "Descripcion", "Precio", "IVA %",
            "Unidad", "Stock", "Rubro"
        ])
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)

        self.btn_nuevo = QPushButton("Nuevo")
        self.btn_editar = QPushButton("Editar")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_actualizar = QPushButton("Actualizar")

        self.btn_nuevo.clicked.connect(self.nuevo_producto)
        self.btn_editar.clicked.connect(self.editar_producto)
        self.btn_eliminar.clicked.connect(self.eliminar_producto)
        self.btn_actualizar.clicked.connect(self.cargar_productos)

        filtro_layout = QHBoxLayout()
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
        self.cargar_productos()

    def cargar_productos(self):
        self.productos_cache = self.module.listar()
        self._poblar_tabla(self.productos_cache)
        if self.buscador.text():
            self.filtrar_tabla(self.buscador.text())

    def _poblar_tabla(self, productos):
        self.tabla.setRowCount(len(productos))
        for fila, producto in enumerate(productos):
            valores = [
                producto["id_producto"], producto["codigo"] or "",
                producto["descripcion"], producto["precio"],
                producto["iva"], producto["unidad"],
                producto["stock"], producto["rubro"] or "",
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

    def producto_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0 or self.tabla.isRowHidden(fila):
            QMessageBox.warning(self, "Seleccion requerida", "Selecciona un producto o servicio.")
            return None
        id_producto = int(self.tabla.item(fila, 0).text())
        for p in self.productos_cache:
            if p["id_producto"] == id_producto:
                return p
        return None

    def nuevo_producto(self):
        dialog = ProductoServicioDialog(self)
        if dialog.exec() == QDialog.Accepted:
            datos = dialog.datos()
            self.module.crear(
                datos["codigo"], datos["descripcion"], datos["precio"],
                datos["iva"], datos["unidad"], datos["stock"], datos["rubro"]
            )
            self.cargar_productos()

    def editar_producto(self):
        producto = self.producto_seleccionado()
        if producto is None:
            return
        dialog = ProductoServicioDialog(self, producto=producto)
        if dialog.exec() == QDialog.Accepted:
            datos = dialog.datos()
            self.module.editar(
                producto["id_producto"], datos["codigo"], datos["descripcion"],
                datos["precio"], datos["iva"], datos["unidad"],
                datos["stock"], datos["rubro"]
            )
            self.cargar_productos()

    def eliminar_producto(self):
        producto = self.producto_seleccionado()
        if producto is None:
            return
        respuesta = QMessageBox.question(self, "Eliminar producto / servicio", "Seguro que queres eliminar este producto o servicio?")
        if respuesta == QMessageBox.Yes:
            self.module.eliminar(producto["id_producto"])
            self.cargar_productos()