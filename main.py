import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from app.styles import APP_STYLE
from app.views.Main_Window import MainWindow


def main():
    app = QApplication(sys.argv)

    # Metadatos de la aplicación
    app.setApplicationName("Intermedios")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("MiEmpresa")

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