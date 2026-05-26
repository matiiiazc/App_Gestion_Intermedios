from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QStackedWidget, QFrame
)
from PySide6.QtCore import Qt

from app.views.clientes_view import ClientesView
from app.views.pedidos_view import PedidosView
from app.views.presupuestos_view import PresupuestosView
from app.views.pagos_view import PagosView
from app.views.gastos_view import GastosView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Intermedios")
        self.showMaximized()

        self.menu = QListWidget()
        self.menu.addItem(QListWidgetItem("Clientes"))
        self.menu.addItem(QListWidgetItem("Pedidos"))
        self.menu.addItem(QListWidgetItem("Presupuestos"))
        self.menu.addItem(QListWidgetItem("Pagos"))
        self.menu.addItem(QListWidgetItem("Gastos"))
        self.menu.currentRowChanged.connect(self.cambiar_pagina)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(200)

        titulo = QLabel("Intermedios")
        titulo.setObjectName("AppTitle")

        subtitulo = QLabel("Gestión comercial")
        subtitulo.setObjectName("AppSubtitle")

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        sidebar_layout.addWidget(titulo)
        sidebar_layout.addWidget(subtitulo)
        sidebar_layout.addWidget(self.menu)
        sidebar_layout.addStretch()
        sidebar.setLayout(sidebar_layout)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.crear_pagina("Clientes",              ClientesView()))
        self.stack.addWidget(self.crear_pagina("Pedidos",               PedidosView()))
        self.stack.addWidget(self.crear_pagina("Presupuestos",          PresupuestosView()))
        self.stack.addWidget(self.crear_pagina("Pagos",                 PagosView()))
        self.stack.addWidget(self.crear_pagina("Gastos",                GastosView()))

        content = QFrame()
        content.setObjectName("Content")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(24, 22, 24, 24)
        content_layout.addWidget(self.stack)
        content.setLayout(content_layout)

        root = QWidget()
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(sidebar)
        root_layout.addWidget(content)
        root.setLayout(root_layout)

        self.setCentralWidget(root)
        self.menu.setCurrentRow(0)

    def crear_pagina(self, titulo, widget):
        pagina = QWidget()
        label  = QLabel(titulo)
        label.setObjectName("PageTitle")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(label)
        layout.addWidget(widget)
        pagina.setLayout(layout)
        return pagina

    def cambiar_pagina(self, index):
        self.stack.setCurrentIndex(index)