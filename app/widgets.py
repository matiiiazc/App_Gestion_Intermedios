"""
Widgets reutilizables para toda la app.
"""

from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Qt


class ComboBoxSinScroll(QComboBox):


    def __init__(self, *args, ancho_minimo_popup=260, max_items_visibles=15, **kwargs):
        super().__init__(*args, **kwargs)

        # Que no tome el foco con la rueda del mouse, solo con click/tab
        self.setFocusPolicy(Qt.StrongFocus)

        # Popup mas grande: mas ancho y mas opciones visibles antes de scrollear
        self.setMaxVisibleItems(max_items_visibles)
        self.view().setMinimumWidth(ancho_minimo_popup)

        # Tipografia un poco mas grande, tanto en el combo como en el popup
        fuente = self.font()
        if fuente.pointSize() > 0:
            fuente.setPointSize(fuente.pointSize() + 1)
        self.setFont(fuente)
        self.view().setFont(fuente)

        # Un poco mas de alto por fila en el popup, mas facil de tocar/leer
        self.view().setStyleSheet("QAbstractItemView::item { padding: 6px 8px; }")

    def wheelEvent(self, event):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()