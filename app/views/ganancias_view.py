from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QGroupBox, QFrame, QDateEdit, QPushButton, QScrollArea
)
from PySide6.QtCore import Qt, QDate

from app.modules.ganancias import GananciasModule


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

        periodo_lay.addWidget(lbl_desde)
        periodo_lay.addWidget(self.fecha_desde)
        periodo_lay.addWidget(lbl_hasta)
        periodo_lay.addWidget(self.fecha_hasta)
        periodo_lay.addWidget(btn_consultar)

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

        root.addWidget(left_w)
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

    def _consultar(self):
        desde = self.fecha_desde.date().toString("yyyy-MM-dd")
        hasta = self.fecha_hasta.date().toString("yyyy-MM-dd")

        pedidos = self.module.get_pedidos_periodo(desde, hasta)
        gastos  = self.module.get_gastos_periodo(desde, hasta)

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
        total_gastos = sum(g["costo"] for g in gastos)
        ganancia_neta = total_ganancia - total_gastos

        self.lbl_gastos.setText(f"Gastos: {_fmt(total_gastos)}")
        self.lbl_ganancia.setText(f"Ganancia: {_fmt(total_ganancia)}")
        color_neta = "#4ade80" if ganancia_neta >= 0 else "#f87171"
        self.lbl_neta.setText(f"Ganancia Neta: {_fmt(ganancia_neta)}")
        self.lbl_neta.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {color_neta}; background: transparent;"
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