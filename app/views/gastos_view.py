from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QLineEdit, QFormLayout, QDialog,
    QDialogButtonBox, QDoubleSpinBox, QDateEdit, QLabel,
    QGroupBox, QScrollArea, QFrame, QListWidget, QComboBox, QTextEdit
)
from PySide6.QtCore import Qt, QDate

from app.modules.gastos import GastosModule, CATEGORIAS


def _fmt(n: float) -> str:
    return f"$ {n:,.0f}".replace(",", ".")


# ==== DIALOG HISTORIAL PROVEEDOR ====

class HistorialProveedorDialog(QDialog):
    def __init__(self, parent, proveedor: str, gastos: list):
        super().__init__(parent)
        self.setWindowTitle(f"Historial — {proveedor}")
        self.resize(660, 420)

        tabla = QTableWidget(0, 5)
        tabla.setHorizontalHeaderLabels(["Producto", "Descripción", "Categoría", "Fecha", "Costo"])
        tabla.verticalHeader().setVisible(False)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.setSelectionBehavior(QTableWidget.SelectRows)
        tabla.setAlternatingRowColors(True)
        tabla.horizontalHeader().setStretchLastSection(True)

        total = 0.0
        tabla.setRowCount(len(gastos))
        for fila, g in enumerate(gastos):
            tabla.setItem(fila, 0, QTableWidgetItem(g["producto"]))
            tabla.setItem(fila, 1, QTableWidgetItem(g["descripcion"] or ""))
            tabla.setItem(fila, 2, QTableWidgetItem(g["categoria"] or ""))
            tabla.setItem(fila, 3, QTableWidgetItem(g["fecha"]))
            tabla.setItem(fila, 4, QTableWidgetItem(_fmt(g["costo"])))
            for col in range(5):
                item = tabla.item(fila, col)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)
            total += g["costo"]

        tabla.resizeColumnsToContents()

        lbl_total = QLabel(f"Total: {_fmt(total)}")
        lbl_total.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #f87171;"
            "background: transparent; padding: 6px 0;"
        )
        lbl_total.setAlignment(Qt.AlignRight)

        btn_cerrar = QDialogButtonBox(QDialogButtonBox.Close)
        btn_cerrar.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addWidget(tabla)
        layout.addWidget(lbl_total)
        layout.addWidget(btn_cerrar)


# ==== DIALOG GASTO ====

class GastoDialog(QDialog):
    def __init__(self, parent=None, gasto=None, proveedores=None):
        super().__init__(parent)
        self.setWindowTitle("Gasto")
        self.setMinimumWidth(400)

        # Producto
        self.producto_input = QLineEdit()

        # Proveedor — combo editable con lista de existentes
        self.proveedor_combo = QComboBox()
        self.proveedor_combo.setEditable(True)
        self.proveedor_combo.addItem("")
        for p in (proveedores or []):
            self.proveedor_combo.addItem(p)
        self.proveedor_combo.setCurrentIndex(0)

        # Descripcion
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setMaximumHeight(80)
        self.descripcion_input.setPlaceholderText("Descripción opcional...")

        # Categoria
        self.categoria_combo = QComboBox()
        self.categoria_combo.addItems(CATEGORIAS)

        # Fecha
        self.fecha_input = QDateEdit()
        self.fecha_input.setCalendarPopup(True)
        self.fecha_input.setDisplayFormat("dd/MM/yyyy")
        self.fecha_input.setDate(QDate.currentDate())

        # Costo
        self.costo_input = QDoubleSpinBox()
        self.costo_input.setMaximum(999_999_999)
        self.costo_input.setDecimals(2)
        self.costo_input.setPrefix("$ ")

        if gasto:
            self.producto_input.setText(gasto["producto"])
            # Setear proveedor en el combo
            prov = gasto["proveedor"] or ""
            idx = self.proveedor_combo.findText(prov)
            if idx >= 0:
                self.proveedor_combo.setCurrentIndex(idx)
            else:
                self.proveedor_combo.setCurrentText(prov)
            self.descripcion_input.setPlainText(gasto["descripcion"] or "")
            cat_idx = self.categoria_combo.findText(gasto["categoria"] or "")
            if cat_idx >= 0:
                self.categoria_combo.setCurrentIndex(cat_idx)
            self.fecha_input.setDate(QDate.fromString(gasto["fecha"], "yyyy-MM-dd"))
            self.costo_input.setValue(gasto["costo"])

        form = QFormLayout()
        form.setSpacing(12)
        form.addRow("Producto:",    self.producto_input)
        form.addRow("Proveedor:",   self.proveedor_combo)
        form.addRow("Descripción:", self.descripcion_input)
        form.addRow("Categoría:",   self.categoria_combo)
        form.addRow("Fecha:",       self.fecha_input)
        form.addRow("Costo:",       self.costo_input)

        botones = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        botones.accepted.connect(self._validar)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.addLayout(form)
        layout.addWidget(botones)

    def _validar(self):
        if not self.producto_input.text().strip():
            QMessageBox.warning(self, "Error", "El producto no puede estar vacío.")
            return
        if self.costo_input.value() <= 0:
            QMessageBox.warning(self, "Error", "El costo debe ser mayor a cero.")
            return
        self.accept()

    def datos(self) -> dict:
        return {
            "producto":    self.producto_input.text().strip(),
            "proveedor":   self.proveedor_combo.currentText().strip(),
            "descripcion": self.descripcion_input.toPlainText().strip(),
            "categoria":   self.categoria_combo.currentText(),
            "fecha":       self.fecha_input.date().toString("yyyy-MM-dd"),
            "costo":       self.costo_input.value(),
        }


# ==== VISTA PRINCIPAL ====

class GastosView(QWidget):
    def __init__(self):
        super().__init__()
        self.module = GastosModule()
        self._setup_ui()
        self._cargar()

    def _setup_ui(self):
        root = QHBoxLayout(self)
        root.setSpacing(20)

        # ==== IZQUIERDA: ACCIONES ====
        left = QVBoxLayout()
        left.setSpacing(10)

        acciones_box = QGroupBox("Acciones")
        acc_layout = QVBoxLayout(acciones_box)
        acc_layout.setSpacing(8)

        btn_nuevo    = QPushButton("Agregar")
        btn_editar   = QPushButton("Editar")
        btn_eliminar = QPushButton("Eliminar")
        btn_buscar   = QPushButton("Buscar proveedor")

        btn_nuevo.clicked.connect(self._nuevo)
        btn_editar.clicked.connect(self._editar)
        btn_eliminar.clicked.connect(self._eliminar)
        btn_buscar.clicked.connect(self._buscar_por_proveedor)

        acc_layout.addWidget(btn_nuevo)
        acc_layout.addWidget(btn_editar)
        acc_layout.addWidget(btn_eliminar)
        acc_layout.addWidget(btn_buscar)

        left.addWidget(acciones_box)
        left.addStretch()

        left_w = QWidget()
        left_w.setLayout(left)
        left_w.setFixedWidth(200)

        # ==== DERECHA ====
        right = QVBoxLayout()
        right.setSpacing(14)

        # ==== SALDOS POR PROVEEDOR ====
        saldos_box = QGroupBox("Saldo por proveedor")
        saldos_outer = QVBoxLayout(saldos_box)
        saldos_outer.setContentsMargins(6, 6, 6, 6)

        self.scroll_saldos = QScrollArea()
        self.scroll_saldos.setWidgetResizable(True)
        self.scroll_saldos.setFixedHeight(180)
        self.scroll_saldos.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.saldos_container = QWidget()
        self.saldos_layout    = QVBoxLayout(self.saldos_container)
        self.saldos_layout.setSpacing(4)
        self.saldos_layout.setContentsMargins(4, 4, 4, 4)
        self.saldos_layout.addStretch()

        self.scroll_saldos.setWidget(self.saldos_container)
        saldos_outer.addWidget(self.scroll_saldos)
        right.addWidget(saldos_box)

        # ==== HISTORIAL ====
        hist_box = QGroupBox("Historial de gastos")
        hist_layout = QVBoxLayout(hist_box)

        self.tabla = QTableWidget(0, 7)
        self.tabla.setHorizontalHeaderLabels(
            ["ID", "Producto", "Proveedor", "Descripción", "Categoría", "Fecha", "Costo"]
        )
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setColumnWidth(0, 50)

        hist_layout.addWidget(self.tabla)
        right.addWidget(hist_box, 1)

        right_w = QWidget()
        right_w.setLayout(right)

        root.addWidget(left_w)
        root.addWidget(right_w, 1)

    def _cargar(self):
        gastos = self.module.listar()

        # ==== TABLA HISTORIAL ====
        self.tabla.setRowCount(len(gastos))
        for fila, g in enumerate(gastos):
            self.tabla.setItem(fila, 0, QTableWidgetItem(str(g["id_gasto"])))
            self.tabla.setItem(fila, 1, QTableWidgetItem(g["producto"]))
            self.tabla.setItem(fila, 2, QTableWidgetItem(g["proveedor"] or ""))
            self.tabla.setItem(fila, 3, QTableWidgetItem(g["descripcion"] or ""))
            self.tabla.setItem(fila, 4, QTableWidgetItem(g["categoria"] or ""))
            self.tabla.setItem(fila, 5, QTableWidgetItem(g["fecha"]))
            self.tabla.setItem(fila, 6, QTableWidgetItem(_fmt(g["costo"])))
            for col in range(7):
                item = self.tabla.item(fila, col)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)
        self.tabla.resizeColumnsToContents()
        self.tabla.setColumnWidth(0, 50)

        # ==== SALDOS POR PROVEEDOR ====
        while self.saldos_layout.count() > 1:
            item = self.saldos_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for prov, total in self.module.get_totales_por_proveedor():
            frame = QFrame()
            frame.setStyleSheet(
                "QFrame { background-color: #1a1a1a; border-radius: 8px; }"
            )
            frame.setCursor(Qt.PointingHandCursor)
            frame.mouseDoubleClickEvent = lambda _, p=prov: self._abrir_historial_proveedor(p)

            fl = QHBoxLayout(frame)
            fl.setContentsMargins(12, 8, 12, 8)

            lbl_nombre = QLabel(prov)
            lbl_nombre.setStyleSheet(
                "font-size: 13px; font-weight: 600; color: #e2e8f0; background: transparent;"
            )
            lbl_total = QLabel(_fmt(total))
            lbl_total.setStyleSheet(
                "font-size: 13px; font-weight: 700; color: #f87171; background: transparent;"
            )
            lbl_total.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            fl.addWidget(lbl_nombre)
            fl.addStretch()
            fl.addWidget(lbl_total)

            self.saldos_layout.insertWidget(self.saldos_layout.count() - 1, frame)

    def _abrir_historial_proveedor(self, proveedor: str):
        gastos_prov = self.module.listar_por_proveedor(proveedor)
        dialog = HistorialProveedorDialog(self, proveedor, gastos_prov)
        dialog.exec()

    def _buscar_por_proveedor(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Buscar proveedor")
        dlg.setMinimumWidth(300)
        campo = QLineEdit()
        campo.setPlaceholderText("Nombre del proveedor...")
        botones = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botones.accepted.connect(dlg.accept)
        botones.rejected.connect(dlg.reject)
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel("Proveedor:"))
        lay.addWidget(campo)
        lay.addWidget(botones)
        if dlg.exec() != QDialog.Accepted:
            return
        busqueda = campo.text().strip().lower()
        if not busqueda:
            return

        coincidencias = [p for p in self.module.get_proveedores()
                         if busqueda in p.lower()]

        if not coincidencias:
            QMessageBox.information(self, "Sin resultados", "No se encontró ningún proveedor.")
            return
        if len(coincidencias) == 1:
            self._abrir_historial_proveedor(coincidencias[0])
        else:
            dlg2 = QDialog(self)
            dlg2.setWindowTitle("Seleccioná un proveedor")
            dlg2.setMinimumWidth(300)
            lista = QListWidget()
            lista.addItems(coincidencias)
            lista.setCurrentRow(0)
            lista.doubleClicked.connect(dlg2.accept)
            bots = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            bots.accepted.connect(dlg2.accept)
            bots.rejected.connect(dlg2.reject)
            lay2 = QVBoxLayout(dlg2)
            lay2.addWidget(lista)
            lay2.addWidget(bots)
            if dlg2.exec() == QDialog.Accepted and lista.currentItem():
                self._abrir_historial_proveedor(lista.currentItem().text())

    def _fila_seleccionada(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Atención", "Seleccioná un gasto primero.")
            return None
        return fila

    def _nuevo(self):
        proveedores = self.module.get_proveedores()
        dialog = GastoDialog(self, proveedores=proveedores)
        if dialog.exec() == QDialog.Accepted:
            d = dialog.datos()
            self.module.crear(d["producto"], d["proveedor"], d["descripcion"],
                              d["categoria"], d["costo"], d["fecha"])
            self._cargar()

    def _editar(self):
        fila = self._fila_seleccionada()
        if fila is None:
            return
        id_gasto  = int(self.tabla.item(fila, 0).text())
        gasto     = self.module.get_gasto(id_gasto)
        if not gasto:
            return
        proveedores = self.module.get_proveedores()
        dialog = GastoDialog(self, gasto=gasto, proveedores=proveedores)
        if dialog.exec() == QDialog.Accepted:
            d = dialog.datos()
            self.module.editar(id_gasto, d["producto"], d["proveedor"], d["descripcion"],
                               d["categoria"], d["costo"], d["fecha"])
            self._cargar()

    def _eliminar(self):
        fila = self._fila_seleccionada()
        if fila is None:
            return
        id_gasto = int(self.tabla.item(fila, 0).text())
        producto = self.tabla.item(fila, 1).text()
        resp = QMessageBox.question(
            self, "Confirmar",
            f"¿Eliminar el gasto «{producto}»?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            self.module.eliminar(id_gasto)
            self._cargar()
