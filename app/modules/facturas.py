from app.db import Database
from app.services.facturacion import autorizar_y_generar_pdf


class FacturasModule:
    def __init__(self):
        self.db = Database()

    def listar(self):
        return self.db.get_facturas()

    def listar_clientes(self):
        return self.db.get_clientes()

    def listar_productos(self):
        return self.db.get_productos_servicios()

    def obtener_detalles(self, id_factura):
        return self.db.get_factura_detalles(id_factura)

    def crear(self, datos_factura, detalles):
        self.db.insertar_factura_con_detalles(datos_factura, detalles)

    def eliminar(self, id_factura):
        self.db.eliminar_factura(id_factura)

    def cerrar(self):
        self.db.cerrar()

    def autorizar_en_arca(self, id_factura: int) -> dict:
        """
        Llama al servicio de facturación para obtener CAE y generar PDF.
        Devuelve dict con 'numero', 'cae', 'cae_vto', 'pdf_path'.
        Lanza excepción si algo falla.
        """
        return autorizar_y_generar_pdf(id_factura)
