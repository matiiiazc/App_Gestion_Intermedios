from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QGroupBox, QFrame, QDateEdit, QPushButton, QScrollArea,
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QDate

from app.modules.ganancias import GananciasModule
from app.modules.ganancias_pdf import generar_pdf_ganancias


def _fmt(n: float) -> str:
    return f"$ {n:,.0f}".replace(",", ".")


class GananciasView(QWidget):
    def __init__(self):
        super().__init__()
        self.module = GananciasModule()
        self._setup_ui()
        self._consultar()

    def _setup_ui(self):
        root = QHBoxLayout(self)
        root.setSpacing(20)

        # ==== IZQUIERDA: FILTRO + RANKING ====
        left = QVBoxLayout()
        left.setSpacing(12)

        # ==== SELECTOR DE PERIODO ====
        periodo_box = QGroupBox("Período")
        periodo_lay = QVBoxLayout(periodo_box)
        periodo_lay.setSpacing(8)

        # accesos rápidos
        accesos_lay = QHBoxLayout()
        accesos_lay.setSpacing(4)
        btn_hoy = QPushButton("Hoy")
        btn_mes_actual = QPushButton("Este mes")
        btn_mes_pasado = QPushButton("Mes pasado")
        btn_hoy.clicked.connect(self._set_periodo_hoy)
        btn_mes_actual.clicked.connect(self._set_periodo_mes_actual)
        btn_mes_pasado.clicked.connect(self._set_periodo_mes_pasado)
        for b in (btn_hoy, btn_mes_actual, btn_mes_pasado):
            b.setStyleSheet("font-size: 11px; padding: 4px;")
        accesos_lay.addWidget(btn_hoy)
        accesos_lay.addWidget(btn_mes_actual)
        accesos_lay.addWidget(btn_mes_pasado)
        periodo_lay.addLayout(accesos_lay)

        lbl_desde = QLabel("Desde:")
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setCalendarPopup(True)
        self.fecha_desde.setDisplayFormat("dd/MM/yyyy")
        self.fecha_desde.setDate(QDate.currentDate().addMonths(-1))

        lbl_hasta = QLabel("Hasta:")
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setCalendarPopup(True)
        self.fecha_hasta.setDisplayFormat("dd/MM/yyyy")
        self.fecha_hasta.setDate(QDate.currentDate())

        btn_consultar = QPushButton("Consultar")
        btn_consultar.clicked.connect(self._consultar)

        btn_exportar_pdf = QPushButton("Exportar PDF")
        btn_exportar_pdf.clicked.connect(self._exportar_pdf)

        periodo_lay.addWidget(lbl_desde)
        periodo_lay.addWidget(self.fecha_desde)
        periodo_lay.addWidget(lbl_hasta)
        periodo_lay.addWidget(self.fecha_hasta)
        periodo_lay.addWidget(btn_consultar)
        periodo_lay.addWidget(btn_exportar_pdf)

        left.addWidget(periodo_box)

        # ==== TOP PROVEEDORES ====
        top_prov_box = QGroupBox("Top 3 proveedores con más gasto")
        top_prov_lay = QVBoxLayout(top_prov_box)
        top_prov_lay.setSpacing(4)
        self.top_prov_layout = top_prov_lay
        left.addWidget(top_prov_box)

        # ==== TOP PRODUCTOS ====
        top_prod_box = QGroupBox("Top 3 trabajos más realizados")
        top_prod_lay = QVBoxLayout(top_prod_box)
        top_prod_lay.setSpacing(4)
        self.top_prod_layout = top_prod_lay
        left.addWidget(top_prod_box)

        left.addStretch()

        # ==== RESUMEN ABAJO IZQUIERDA ====
        resumen_frame = QFrame()
        resumen_frame.setStyleSheet(
            "QFrame { background-color: #111; border-radius: 10px; border: 1px solid #2a2a2a; }"
        )
        resumen_lay = QVBoxLayout(resumen_frame)
        resumen_lay.setContentsMargins(16, 14, 16, 14)
        resumen_lay.setSpacing(8)

        self.lbl_gastos    = QLabel("Gastos: $ 0")
        self.lbl_ganancia  = QLabel("Ganancia: $ 0")
        self.lbl_neta      = QLabel("Ganancia Neta: $ 0")

        for lbl in (self.lbl_gastos, self.lbl_ganancia):
            lbl.setStyleSheet("font-size: 15px; color: #cbd5e1; background: transparent;")

        self.lbl_neta.setStyleSheet(
            "font-size: 18px; font-weight: 700; color: #4ade80; background: transparent;"
        )

        resumen_lay.addWidget(self.lbl_gastos)
        resumen_lay.addWidget(self.lbl_ganancia)
        resumen_lay.addWidget(self.lbl_neta)

        left.addWidget(resumen_frame)

        left_w = QWidget()
        left_w.setLayout(left)
        left_w.setFixedWidth(240)

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_scroll.setFrameShape(QScrollArea.NoFrame)
        left_scroll.setWidget(left_w)
        left_scroll.setFixedWidth(258)  # ancho del contenido + lugar para la barra de scroll

        # ==== DERECHA: TABLAS ====
        right = QVBoxLayout()
        right.setSpacing(14)

        # ==== TABLA TRABAJOS ====
        trabajos_box = QGroupBox("Trabajos del período")
        trabajos_outer = QVBoxLayout(trabajos_box)
        trabajos_outer.setContentsMargins(6, 6, 6, 6)

        self.scroll_trabajos = QScrollArea()
        self.scroll_trabajos.setWidgetResizable(True)
        self.scroll_trabajos.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.trabajos_container = QWidget()
        self.trabajos_layout    = QVBoxLayout(self.trabajos_container)
        self.trabajos_layout.setSpacing(4)
        self.trabajos_layout.setContentsMargins(4, 4, 4, 4)
        self.trabajos_layout.setAlignment(Qt.AlignTop)

        self.scroll_trabajos.setWidget(self.trabajos_container)
        trabajos_outer.addWidget(self.scroll_trabajos)
        right.addWidget(trabajos_box, 1)

        right_w = QWidget()
        right_w.setLayout(right)

        root.addWidget(left_scroll)
        root.addWidget(right_w, 1)

    def _limpiar_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _hacer_fila_ranking(self, pos: str, nombre: str, valor: str) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("QFrame { background-color: #1a1a1a; border-radius: 6px; }")
        fl = QHBoxLayout(frame)
        fl.setContentsMargins(10, 6, 10, 6)

        lbl_pos    = QLabel(pos)
        lbl_nombre = QLabel(nombre)
        lbl_valor  = QLabel(valor)

        lbl_pos.setStyleSheet(
            "font-size: 13px; font-weight: 700; color: #facc15; background: transparent;"
        )
        lbl_nombre.setStyleSheet(
            "font-size: 12px; color: #e2e8f0; background: transparent;"
        )
        lbl_valor.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #f87171; background: transparent;"
        )
        lbl_valor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        fl.addWidget(lbl_pos)
        fl.addWidget(lbl_nombre, 1)
        fl.addWidget(lbl_valor)
        return frame

    def _set_periodo_hoy(self):
        hoy = QDate.currentDate()
        self.fecha_desde.setDate(hoy)
        self.fecha_hasta.setDate(hoy)
        self._consultar()

    def _set_periodo_mes_actual(self):
        hoy = QDate.currentDate()
        primero_del_mes = QDate(hoy.year(), hoy.month(), 1)
        self.fecha_desde.setDate(primero_del_mes)
        self.fecha_hasta.setDate(hoy)
        self._consultar()

    def _set_periodo_mes_pasado(self):
        hoy = QDate.currentDate()
        primero_mes_actual = QDate(hoy.year(), hoy.month(), 1)
        ultimo_mes_pasado = primero_mes_actual.addDays(-1)
        primero_mes_pasado = QDate(ultimo_mes_pasado.year(), ultimo_mes_pasado.month(), 1)
        self.fecha_desde.setDate(primero_mes_pasado)
        self.fecha_hasta.setDate(ultimo_mes_pasado)
        self._consultar()

    def _consultar(self):
        desde = self.fecha_desde.date().toString("yyyy-MM-dd")
        hasta = self.fecha_hasta.date().toString("yyyy-MM-dd")

        pedidos = self.module.get_pedidos_periodo(desde, hasta)
        gastos  = self.module.get_gastos_periodo(desde, hasta)

        # guardamos el estado de la última consulta para poder exportarlo a PDF
        self._ultimo_desde = desde
        self._ultimo_hasta = hasta
        self._ultimos_pedidos = pedidos
        self._ultimo_total_gastos = sum(g["costo"] for g in gastos)

        # ==== LISTA TRABAJOS ====
        self._limpiar_layout(self.trabajos_layout)
        total_ganancia = 0.0
        for p in pedidos:
            frame = QFrame()
            frame.setStyleSheet("QFrame { background-color: #1a1a1a; border-radius: 8px; }")
            frame.setFixedHeight(52)
            fl = QHBoxLayout(frame)
            fl.setContentsMargins(12, 6, 12, 6)

            lbl_cliente  = QLabel(p["cliente"])
            lbl_trabajo  = QLabel(p["tipo_trabajo"])
            lbl_fecha    = QLabel(p["fecha"])
            lbl_final    = QLabel(_fmt(p["precio_final"] or 0))

            lbl_cliente.setStyleSheet("font-size: 13px; font-weight: 600; color: #e2e8f0; background: transparent;")
            lbl_trabajo.setStyleSheet("font-size: 12px; color: #94a3b8; background: transparent;")
            lbl_fecha.setStyleSheet("font-size: 12px; color: #64748b; background: transparent;")
            lbl_final.setStyleSheet("font-size: 13px; font-weight: 700; color: #4ade80; background: transparent;")
            lbl_final.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            fl.addWidget(lbl_cliente, 2)
            fl.addWidget(lbl_trabajo, 2)
            fl.addWidget(lbl_fecha, 1)
            fl.addWidget(lbl_final, 1)

            self.trabajos_layout.insertWidget(self.trabajos_layout.count() - 1, frame)
            total_ganancia += p["precio_final"] or 0

        # ==== RESUMEN ====
        total_gastos = self._ultimo_total_gastos
        ganancia_neta = total_ganancia - total_gastos

        self.lbl_gastos.setText(f"Gastos: {_fmt(total_gastos)}")
        self.lbl_ganancia.setText(f"Ganancia: {_fmt(total_ganancia)}")
        color_neta = "#4ade80" if ganancia_neta >= 0 else "#f87171"
        self.lbl_neta.setText(f"Ganancia Neta: {_fmt(ganancia_neta)}")
        self.lbl_neta.setStyleSheet(
            f"font-size: 10px; font-weight: 700; color: {color_neta}; background: transparent;"
        )

        # ==== TOP PROVEEDORES ====
        self._limpiar_layout(self.top_prov_layout)
        medallas = ["1.", "2.", "3."]
        for i, row in enumerate(self.module.get_top_proveedores(3)):
            frame = self._hacer_fila_ranking(
                medallas[i], row["proveedor"], _fmt(row["total"])
            )
            self.top_prov_layout.addWidget(frame)

        # ==== TOP PRODUCTOS ====
        self._limpiar_layout(self.top_prod_layout)
        for i, row in enumerate(self.module.get_top_productos(3)):
            frame = self._hacer_fila_ranking(
                medallas[i],
                row["producto"],
                f"{row['cantidad']} trabajos · {_fmt(row['total'])}"
            )
            self.top_prod_layout.addWidget(frame)

    # ==== EXPORTAR PDF ====
    def _exportar_pdf(self):
        if not hasattr(self, "_ultimos_pedidos"):
            QMessageBox.warning(self, "Sin datos", "Primero hacé una consulta.")
            return

        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar reporte", "reporte_ganancias.pdf", "PDF (*.pdf)"
        )
        if not ruta:
            return

        total_ganancia = sum(p["precio_final"] or 0 for p in self._ultimos_pedidos)
        ganancia_neta = total_ganancia - self._ultimo_total_gastos

        generar_pdf_ganancias(
            fecha_desde=self._ultimo_desde,
            fecha_hasta=self._ultimo_hasta,
            pedidos=self._ultimos_pedidos,
            total_gastos=self._ultimo_total_gastos,
            total_ganancia=total_ganancia,
            ganancia_neta=ganancia_neta,
            top_proveedores=self.module.get_top_proveedores(3),
            top_productos=self.module.get_top_productos(3),
            ruta_salida=ruta,
        )
        QMessageBox.information(self, "Listo", "Reporte exportado correctamente.")