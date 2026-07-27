import os
import sys

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "PassThrough"

if sys.platform.startswith("win"):
    import ctypes
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "intermedios.gestion_comercial.1"
        )
    except Exception:
        pass

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon

from app.styles import APP_STYLE
from app.views.Main_Window import MainWindow
from app.modules.orden_pedido_pdf import get_base_path


def main():
    app = QApplication(sys.argv)

    # Metadatos de la aplicación
    app.setApplicationName("Intermedios")

    ruta_logo = get_base_path() / "assets" / "logo.png"
    if ruta_logo.exists():
        app.setWindowIcon(QIcon(str(ruta_logo)))

    app.setStyleSheet(APP_STYLE)

    try:
        window = MainWindow()
        window.show()
    except Exception as e:
        error_dialog = QMessageBox()
        error_dialog.setWindowTitle("Error al iniciar")
        error_dialog.setText("No se pudo iniciar la aplicación.")
        error_dialog.setDetailedText(str(e))
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.exec()
        sys.exit(1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()