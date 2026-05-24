from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDialog, QFormLayout, QDoubleSpinBox, QComboBox,
    QDialogButtonBox, QGroupBox, QTableWidget, QTableWidgetItem,
    QGridLayout, QFrame, QSizePolicy, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QFont

from app.modules.pagos import PagosModule, EMPLEADOS, TARIFA_HORA


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt(n: float) -> str:
    return f"$ {n:,.0f}".replace(",", ".")


# ── Dialog: Horas del día ─────────────────────────────────────────────────────

class HorasDialog(QDialog):
    def __init__(self, parent, fecha: str, horas_actuales: dict):
        super().__init__(parent)
        self.setWindowTitle(f"Horas — {fecha}")
        self.setMinimumWidth(320)
        self.fecha = fecha

        self.spins = {}
        form = QFormLayout()

        for emp in EMPLEADOS:
            spin = QDoubleSpinBox()
            spin.setMinimum(0)
            spin.setMaximum(24)
            spin.setDecimals(1)
            spin.setSingleStep(0.5)
            spin.setValue(horas_actuales.get(emp, 0.0))
            spin.setSuffix(" hs")
            self.spins[emp] = spin
            form.addRow(f"{emp}:", spin)

        # Botón mismo horario
        btn_mismo = QPushButton("⟳  Mismo horario para ambos")
        btn_mismo.clicked.connect(self._mismo_horario)

        # Subtotales
        self.lbl_subtotales = QLabel()
        self._actualizar_subtotales()
        for spin in self.spins.values():
            spin.valueChanged.connect(self._actualizar_subtotales)

        botones = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        botones.accepted.connect(self.accept)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(btn_mismo)
        layout.addWidget(self.lbl_subtotales)
        layout.addWidget(botones)

    def _mismo_horario(self):
        """Copia las horas del primero al segundo."""
        horas = self.spins[EMPLEADOS[0]].value()
        for spin in self.spins.values():
            spin.setValue(horas)

    def _actualizar_subtotales(self):
        lineas = []
        for emp, spin in self.spins.items():
            total = spin.value() * TARIFA_HORA
            lineas.append(f"{emp}: {spin.value()} hs → {_fmt(total)}")
        self.lbl_subtotales.setText("\n".join(lineas))

    def datos(self) -> dict:
        return {emp: spin.value() for emp, spin in self.spins.items()}


# ── Dialog: Registrar pago ────────────────────────────────────────────────────

class PagoDialog(QDialog):
    def __init__(self, parent, saldos: dict):
        super().__init__(parent)
        self.setWindowTitle("Registrar pago")
        self.setMinimumWidth(300)

        self.combo_emp = QComboBox()
        self.combo_emp.addItems(EMPLEADOS)
        self.combo_emp.currentTextChanged.connect(self._actualizar_pendiente)

        self.lbl_pendiente = QLabel()

        self.spin_monto = QDoubleSpinBox()
        self.spin_monto.setMaximum(99_999_999)
        self.spin_monto.setDecimals(0)
        self.spin_monto.setSingleStep(1000)
        self.spin_monto.setPrefix("$ ")

        self.combo_modal = QComboBox()
        self.combo_modal.addItems(["Efectivo", "Transferencia"])

        self.saldos = saldos
        self._actualizar_pendiente(EMPLEADOS[0])

        form = QFormLayout()
        form.addRow("Empleado:", self.combo_emp)
        form.addRow("Saldo pendiente:", self.lbl_pendiente)
        form.addRow("Monto a pagar:", self.spin_monto)
        form.addRow("Modalidad:", self.combo_modal)

        botones = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        botones.accepted.connect(self._validar)
        botones.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(botones)

    def _actualizar_pendiente(self, emp: str):
        pendiente = self.saldos.get(emp, {}).get("pendiente", 0)
        self.lbl_pendiente.setText(_fmt(pendiente))
        self.spin_monto.setValue(pendiente if pendiente > 0 else 0)

    def _validar(self):
        if self.spin_monto.value() <= 0:
            QMessageBox.warning(self, "Error", "El monto debe ser mayor a cero.")
            return
        self.accept()

    def datos(self) -> dict:
        return {
            "empleado":  self.combo_emp.currentText(),
            "monto":     self.spin_monto.value(),
            "modalidad": self.combo_modal.currentText(),
        }


# ── Calendario estilo Win11 ───────────────────────────────────────────────────

class CalendarioWidget(QWidget):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view
        self.hoy = QDate.currentDate()
        self.mes_actual = QDate(self.hoy.year(), self.hoy.month(), 1)
        self.dias_con_horas: set = set()

        self._setup_ui()
        self._renderizar()

    def _setup_ui(self):
        self.layout_main = QVBoxLayout(self)
        self.layout_main.setSpacing(6)

        # Navegación mes
        nav = QHBoxLayout()
        self.btn_prev = QPushButton("‹")
        self.btn_prev.setFixedSize(32, 32)
        self.btn_next = QPushButton("›")
        self.btn_next.setFixedSize(32, 32)
        self.lbl_mes = QLabel()
        self.lbl_mes.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        self.lbl_mes.setFont(font)

        self.btn_prev.clicked.connect(self._mes_anterior)
        self.btn_next.clicked.connect(self._mes_siguiente)

        nav.addWidget(self.btn_prev)
        nav.addWidget(self.lbl_mes, 1)
        nav.addWidget(self.btn_next)
        self.layout_main.addLayout(nav)

        # Grid días
        self.grid = QGridLayout()
        self.grid.setSpacing(4)
        self.layout_main.addLayout(self.grid)

    def _mes_anterior(self):
        self.mes_actual = self.mes_actual.addMonths(-1)
        self._renderizar()

    def _mes_siguiente(self):
        self.mes_actual = self.mes_actual.addMonths(1)
        self._renderizar()

    def _renderizar(self):
        # Limpiar grid
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.lbl_mes.setText(
            self.mes_actual.toString("MMMM yyyy").capitalize()
        )

        # Cargar días con horas del mes
        self.dias_con_horas = set(
            self.parent_view.module.get_dias_con_horas(
                self.mes_actual.year(), self.mes_actual.month()
            )
        )

        # Cabecera días semana
        dias_sem = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sa", "Do"]
        for col, d in enumerate(dias_sem):
            lbl = QLabel(d)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #6366f1; font-weight: 700; font-size: 11px;")
            self.grid.addWidget(lbl, 0, col)

        # Primer día del mes (0=lunes en Qt dayOfWeek: 1=lunes...7=domingo)
        primer_dia = self.mes_actual
        col_inicio = primer_dia.dayOfWeek() - 1  # 0-based

        dias_en_mes = primer_dia.daysInMonth()
        fila = 1
        col  = col_inicio

        for dia in range(1, dias_en_mes + 1):
            fecha = QDate(self.mes_actual.year(), self.mes_actual.month(), dia)
            fecha_str = fecha.toString("yyyy-MM-dd")

            btn = QPushButton(str(dia))
            btn.setFixedSize(40, 40)
            btn.setCursor(Qt.PointingHandCursor)

            # Estilo según estado
            es_hoy        = fecha == self.hoy
            tiene_horas   = fecha_str in self.dias_con_horas
            es_fin_semana = fecha.dayOfWeek() >= 6

            if es_hoy:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #6366f1;
                        color: white;
                        border-radius: 20px;
                        font-weight: 700;
                        font-size: 13px;
                    }
                    QPushButton:hover { background-color: #4f46e5; }
                """)
            elif tiene_horas:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #14532d;
                        color: #86efac;
                        border-radius: 20px;
                        font-size: 13px;
                        border: 1px solid #166534;
                    }
                    QPushButton:hover { background-color: #166534; }
                """)
            elif es_fin_semana:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #555555;
                        border-radius: 20px;
                        font-size: 13px;
                        border: none;
                    }
                    QPushButton:hover { background-color: #1e1e1e; color: #e2e8f0; }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #e2e8f0;
                        border-radius: 20px;
                        font-size: 13px;
                        border: none;
                    }
                    QPushButton:hover { background-color: #1e1e1e; }
                """)

            btn.clicked.connect(lambda _, f=fecha_str: self._click_dia(f))
            self.grid.addWidget(btn, fila, col)

            col += 1
            if col > 6:
                col = 0
                fila += 1

    def _click_dia(self, fecha_str: str):
        self.parent_view.abrir_form_horas(fecha_str)

    def refrescar(self):
        self._renderizar()


# ── Vista principal de Pagos ──────────────────────────────────────────────────

class PagosView(QWidget):
    def __init__(self):
        super().__init__()
        self.module = PagosModule()
        self._setup_ui()
        self._actualizar_saldos()

    def _setup_ui(self):
        root = QHBoxLayout(self)
        root.setSpacing(20)

        # ── Columna izquierda: Calendario ─────────────────────────────────
        left = QVBoxLayout()

        cal_box = QGroupBox("Calendario")
        cal_layout = QVBoxLayout(cal_box)
        self.calendario = CalendarioWidget(self)
        cal_layout.addWidget(self.calendario)

        lbl_ref = QLabel("🟣 Hoy   🟢 Con horas cargadas")
        lbl_ref.setStyleSheet("font-size: 11px; color: #555555;")
        cal_layout.addWidget(lbl_ref)

        left.addWidget(cal_box)
        left.addStretch()

        # ── Columna derecha: Saldos + Historial ───────────────────────────
        right = QVBoxLayout()

        # Saldos
        saldos_box = QGroupBox("Saldos")
        saldos_layout = QVBoxLayout(saldos_box)

        self.saldo_widgets = {}
        for emp in EMPLEADOS:
            emp_frame = QFrame()
            emp_frame.setStyleSheet(
                "background-color: #1a1a1a; border-radius: 8px; padding: 4px;"
            )
            emp_layout = QGridLayout(emp_frame)

            lbl_nombre = QLabel(emp)
            lbl_nombre.setStyleSheet("font-size: 14px; font-weight: 700; color: #e2e8f0;")

            lbl_devengado = QLabel("Devengado: —")
            lbl_devengado.setStyleSheet("color: #94a3b8; font-size: 11px;")
            lbl_pagado    = QLabel("Pagado: —")
            lbl_pagado.setStyleSheet("color: #94a3b8; font-size: 11px;")
            lbl_pendiente = QLabel("—")
            lbl_pendiente.setStyleSheet(
                "font-size: 18px; font-weight: 700; color: #f87171;"
            )
            lbl_pendiente.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            emp_layout.addWidget(lbl_nombre,    0, 0)
            emp_layout.addWidget(lbl_pendiente, 0, 1, 2, 1)
            emp_layout.addWidget(lbl_devengado, 1, 0)
            emp_layout.addWidget(lbl_pagado,    2, 0)

            self.saldo_widgets[emp] = {
                "devengado": lbl_devengado,
                "pagado":    lbl_pagado,
                "pendiente": lbl_pendiente,
            }
            saldos_layout.addWidget(emp_frame)

        btn_pagar = QPushButton("💸  Registrar pago")
        btn_pagar.clicked.connect(self._registrar_pago)
        saldos_layout.addWidget(btn_pagar)
        right.addWidget(saldos_box)

        # Historial
        hist_box = QGroupBox("Últimos registros")
        hist_layout = QVBoxLayout(hist_box)

        self.combo_hist_emp = QComboBox()
        self.combo_hist_emp.addItems(EMPLEADOS)
        self.combo_hist_emp.currentTextChanged.connect(self._cargar_historial)

        self.tabla_hist = QTableWidget(0, 4)
        self.tabla_hist.setHorizontalHeaderLabels(["Fecha", "Horas", "Total", "Tipo"])
        self.tabla_hist.verticalHeader().setVisible(False)
        self.tabla_hist.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_hist.setAlternatingRowColors(True)
        self.tabla_hist.horizontalHeader().setStretchLastSection(True)

        hist_layout.addWidget(self.combo_hist_emp)
        hist_layout.addWidget(self.tabla_hist)
        right.addWidget(hist_box)

        # Armar root
        left_w  = QWidget(); left_w.setLayout(left)
        right_w = QWidget(); right_w.setLayout(right)
        left_w.setFixedWidth(340)

        root.addWidget(left_w)
        root.addWidget(right_w, 1)

        self._cargar_historial(EMPLEADOS[0])

    # ── Acciones ──────────────────────────────────────────────────────────

    def abrir_form_horas(self, fecha_str: str):
        horas_actuales = self.module.get_horas_fecha(fecha_str)
        dialog = HorasDialog(self, fecha_str, horas_actuales)
        if dialog.exec() == QDialog.Accepted:
            self.module.guardar_horas(fecha_str, dialog.datos())
            self.calendario.refrescar()
            self._actualizar_saldos()
            self._cargar_historial(self.combo_hist_emp.currentText())

    def _registrar_pago(self):
        saldos = {
            emp: self.module.get_saldo(emp) for emp in EMPLEADOS
        }
        dialog = PagoDialog(self, saldos)
        if dialog.exec() == QDialog.Accepted:
            d = dialog.datos()
            self.module.registrar_pago(d["empleado"], d["monto"], d["modalidad"])
            self._actualizar_saldos()
            self._cargar_historial(self.combo_hist_emp.currentText())
            QMessageBox.information(
                self, "Pago registrado",
                f"Se registró un pago de {_fmt(d['monto'])} "
                f"a {d['empleado']} en {d['modalidad']}."
            )

    def _actualizar_saldos(self):
        for emp in EMPLEADOS:
            s = self.module.get_saldo(emp)
            w = self.saldo_widgets[emp]
            w["devengado"].setText(f"Devengado: {_fmt(s['devengado'])}")
            w["pagado"].setText(f"Pagado: {_fmt(s['pagado'])}")
            color = "#f87171" if s["pendiente"] > 0 else "#86efac"
            w["pendiente"].setText(_fmt(s["pendiente"]))
            w["pendiente"].setStyleSheet(
                f"font-size: 18px; font-weight: 700; color: {color};"
            )

    def _cargar_historial(self, empleado: str):
        horas = self.module.get_historial_horas(empleado)
        self.tabla_hist.setRowCount(len(horas))
        for fila, h in enumerate(horas):
            self.tabla_hist.setItem(fila, 0, QTableWidgetItem(h["fecha"]))
            self.tabla_hist.setItem(fila, 1, QTableWidgetItem(f"{h['horas']} hs"))
            self.tabla_hist.setItem(fila, 2, QTableWidgetItem(_fmt(h["total"])))
            self.tabla_hist.setItem(fila, 3, QTableWidgetItem("Horas"))
            for col in range(4):
                if self.tabla_hist.item(fila, col):
                    self.tabla_hist.item(fila, col).setTextAlignment(Qt.AlignCenter)
        self.tabla_hist.resizeColumnsToContents()