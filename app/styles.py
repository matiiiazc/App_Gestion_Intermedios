APP_STYLE = """
/* ── Base ─────────────────────────────────────────────────────────────── */
QMainWindow {
    background-color: #0d0d0d;
}

QWidget {
    font-family: "Segoe UI";
    font-size: 13px;
    color: #e2e8f0;
    background-color: transparent;
}

/* ── Sidebar ──────────────────────────────────────────────────────────── */
#Sidebar {
    background-color: #111111;
    border-right: 1px solid #1e1e1e;
    min-width: 200px;
    max-width: 200px;
}

#AppTitle {
    color: #ffffff;
    font-size: 18px;
    font-weight: 700;
    padding: 22px 20px 2px 20px;
    letter-spacing: 0.5px;
}

#AppSubtitle {
    color: #555555;
    font-size: 11px;
    padding: 0 20px 20px 20px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* Nav list */
QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
    padding: 6px 10px;
}

QListWidget::item {
    color: #888888;
    padding: 12px 14px;
    border-radius: 10px;
    margin: 3px 0;
    font-weight: 500;
    font-size: 13px;
}

QListWidget::item:hover {
    background-color: #1a1a1a;
    color: #e2e8f0;
}

QListWidget::item:selected {
    background-color: #1d1d1d;
    color: #ffffff;
    font-weight: 600;
    border-left: 3px solid #6366f1;
    padding-left: 11px;
}

/* ── Content area ─────────────────────────────────────────────────────── */
#Content {
    background-color: #141414;
}

#PageTitle {
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
    padding-bottom: 6px;
    letter-spacing: -0.3px;
}

/* ── Buttons ──────────────────────────────────────────────────────────── */
QPushButton {
    background-color: #1e1e1e;
    color: #e2e8f0;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 600;
    font-size: 12px;
    letter-spacing: 0.2px;
    min-height: 32px;
}

QPushButton:hover {
    background-color: #2a2a2a;
    border-color: #3a3a3a;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #111111;
}

/* Botón primario — Nueva / Guardar */
QPushButton[text="Nuevo"],
QPushButton[text="Nueva"],
QPushButton[text="Guardar"],
QPushButton[text="Aceptar"],
QPushButton[text="Agregar item"] {
    background-color: #6366f1;
    color: #ffffff;
    border: none;
}

QPushButton[text="Nuevo"]:hover,
QPushButton[text="Nueva"]:hover,
QPushButton[text="Guardar"]:hover,
QPushButton[text="Aceptar"]:hover,
QPushButton[text="Agregar item"]:hover {
    background-color: #4f46e5;
}

/* Botón peligro — Eliminar */
QPushButton[text="Eliminar"],
QPushButton[text="Quitar item"] {
    background-color: #1e1e1e;
    color: #f87171;
    border: 1px solid #3a1f1f;
}

QPushButton[text="Eliminar"]:hover,
QPushButton[text="Quitar item"]:hover {
    background-color: #2d1515;
    border-color: #f87171;
    color: #fca5a5;
}

/* Botón ARCA */
QPushButton[text="🔐 Autorizar en ARCA"] {
    background-color: #14532d;
    color: #86efac;
    border: 1px solid #166534;
}

QPushButton[text="🔐 Autorizar en ARCA"]:hover {
    background-color: #166534;
    color: #bbf7d0;
}

/* Botón PDF */
QPushButton[text="📄 Generar PDF"] {
    background-color: #1e3a5f;
    color: #93c5fd;
    border: 1px solid #1e40af;
}

QPushButton[text="📄 Generar PDF"]:hover {
    background-color: #1e40af;
    color: #bfdbfe;
}

/* Actualizar / secundario */
QPushButton[text="Actualizar"],
QPushButton[text="Editar"],
QPushButton[text="Aceptar presupuesto"] {
    background-color: #1e1e1e;
    color: #a5b4fc;
    border: 1px solid #2e2e4a;
}

QPushButton[text="Actualizar"]:hover,
QPushButton[text="Editar"]:hover,
QPushButton[text="Aceptar presupuesto"]:hover {
    background-color: #252540;
    color: #c7d2fe;
}

/* ── Tabla ────────────────────────────────────────────────────────────── */
QTableWidget {
    background-color: #111111;
    alternate-background-color: #161616;
    gridline-color: #1e1e1e;
    border: 1px solid #1e1e1e;
    border-radius: 10px;
    color: #cbd5e1;
    selection-background-color: #1e1b4b;
    selection-color: #ffffff;
    outline: none;
}

QTableWidget::item {
    padding: 10px 8px;
    border-bottom: 1px solid #1a1a1a;
}

QTableWidget::item:selected {
    background-color: #1e1b4b;
    color: #ffffff;
}

QHeaderView {
    background-color: #111111;
}

QHeaderView::section {
    background-color: #0d0d0d;
    color: #555555;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    padding: 10px 8px;
    border: none;
    border-bottom: 1px solid #1e1e1e;
    border-right: 1px solid #1a1a1a;
}

QTableCornerButton::section {
    background-color: #0d0d0d;
    border: none;
    border-right: 1px solid #1e1e1e;
    border-bottom: 1px solid #1e1e1e;
}

/* ── Inputs ───────────────────────────────────────────────────────────── */
QLineEdit,
QTextEdit,
QComboBox,
QDateEdit,
QSpinBox,
QDoubleSpinBox {
    background-color: #1a1a1a;
    color: #e2e8f0;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 8px 10px;
    selection-background-color: #6366f1;
    min-height: 32px;
}

QLineEdit:focus,
QTextEdit:focus,
QComboBox:focus,
QDateEdit:focus,
QSpinBox:focus,
QDoubleSpinBox:focus {
    border: 1px solid #6366f1;
    background-color: #1d1d2e;
}

QComboBox QAbstractItemView {
    background-color: #1a1a1a;
    color: #e2e8f0;
    selection-background-color: #4f46e5;
    border: 1px solid #2a2a2a;
    outline: none;
}

QComboBox::drop-down,
QDateEdit::drop-down {
    border: none;
    background-color: transparent;
    width: 24px;
}

QSpinBox::up-button,
QSpinBox::down-button,
QDoubleSpinBox::up-button,
QDoubleSpinBox::down-button {
    border: none;
    background-color: #222222;
    width: 20px;
}

/* ── Dialogs ──────────────────────────────────────────────────────────── */
QDialog {
    background-color: #141414;
}

QMessageBox {
    background-color: #141414;
}

QDialogButtonBox QPushButton {
    min-width: 80px;
}

/* ── Labels ───────────────────────────────────────────────────────────── */
QLabel {
    color: #94a3b8;
    background-color: transparent;
}

/* ── GroupBox ─────────────────────────────────────────────────────────── */
QGroupBox {
    border: 1px solid #1e1e1e;
    border-radius: 10px;
    margin-top: 14px;
    padding: 14px;
    font-weight: 600;
    color: #e2e8f0;
    background-color: #111111;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
    color: #6366f1;
}

/* ── Scrollbar ────────────────────────────────────────────────────────── */
QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    margin: 4px 0;
}

QScrollBar::handle:vertical {
    background-color: #2a2a2a;
    min-height: 28px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #3a3a3a;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    height: 0;
    background: none;
    border: none;
}

QScrollBar:horizontal {
    background-color: transparent;
    height: 8px;
    margin: 0 4px;
}

QScrollBar::handle:horizontal {
    background-color: #2a2a2a;
    min-width: 28px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #3a3a3a;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    width: 0;
    background: none;
    border: none;
}
"""