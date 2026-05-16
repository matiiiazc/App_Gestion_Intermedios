from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QSpinBox
)

from app.modules.emisor import EmisorModule


class EmisorView(QWidget):
    def __init__(self):
        super().__init__()

        self.module = EmisorModule()

        self.razon_social_input = QLineEdit()
        self.nombre_fantasia_input = QLineEdit()
        self.cuit_input = QLineEdit()
        self.condicion_iva_input = QLineEdit()
        self.domicilio_input = QLineEdit()
        self.inicio_actividades_input = QLineEdit()
        self.punto_venta_input = QSpinBox()
        self.punto_venta_input.setMinimum(1)
        self.punto_venta_input.setMaximum(99999)
        self.ingresos_brutos_input = QLineEdit()
        self.certificado_mipyme_input = QLineEdit()
        self.email_input = QLineEdit()
        self.telefono_input = QLineEdit()

        form = QFormLayout()
        form.addRow("Razon social:", self.razon_social_input)
        form.addRow("Nombre fantasia:", self.nombre_fantasia_input)
        form.addRow("CUIT:", self.cuit_input)
        form.addRow("Condicion IVA:", self.condicion_iva_input)
        form.addRow("Domicilio:", self.domicilio_input)
        form.addRow("Inicio actividades:", self.inicio_actividades_input)
        form.addRow("Punto venta:", self.punto_venta_input)
        form.addRow("Ingresos brutos:", self.ingresos_brutos_input)
        form.addRow("Certificado MiPyME:", self.certificado_mipyme_input)
        form.addRow("Email:", self.email_input)
        form.addRow("Telefono:", self.telefono_input)

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.guardar)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(self.btn_guardar)
        layout.addStretch()

        self.setLayout(layout)
        self.cargar()

    def cargar(self):
        emisor = self.module.obtener()

        if not emisor:
            return

        self.razon_social_input.setText(emisor["razon_social"] or "")
        self.nombre_fantasia_input.setText(emisor["nombre_fantasia"] or "")
        self.cuit_input.setText(emisor["cuit"] or "")
        self.condicion_iva_input.setText(emisor["condicion_iva"] or "")
        self.domicilio_input.setText(emisor["domicilio"] or "")
        self.inicio_actividades_input.setText(emisor["inicio_actividades"] or "")
        self.punto_venta_input.setValue(int(emisor["punto_venta"] or 1))
        self.ingresos_brutos_input.setText(emisor["ingresos_brutos"] or "")
        self.certificado_mipyme_input.setText(emisor["certificado_mipyme"] or "")
        self.email_input.setText(emisor["email"] or "")
        self.telefono_input.setText(emisor["telefono"] or "")

    def guardar(self):
        if not self.razon_social_input.text().strip():
            QMessageBox.warning(self, "Datos incompletos", "La razon social es obligatoria.")
            return

        if not self.cuit_input.text().strip():
            QMessageBox.warning(self, "Datos incompletos", "El CUIT es obligatorio.")
            return

        datos = {
            "razon_social": self.razon_social_input.text().strip(),
            "nombre_fantasia": self.nombre_fantasia_input.text().strip(),
            "cuit": self.cuit_input.text().strip(),
            "condicion_iva": self.condicion_iva_input.text().strip(),
            "domicilio": self.domicilio_input.text().strip(),
            "inicio_actividades": self.inicio_actividades_input.text().strip(),
            "punto_venta": self.punto_venta_input.value(),
            "ingresos_brutos": self.ingresos_brutos_input.text().strip(),
            "certificado_mipyme": self.certificado_mipyme_input.text().strip(),
            "email": self.email_input.text().strip(),
            "telefono": self.telefono_input.text().strip(),
        }

        self.module.guardar(datos)
        QMessageBox.information(self, "Guardado", "Datos del emisor guardados correctamente.")
