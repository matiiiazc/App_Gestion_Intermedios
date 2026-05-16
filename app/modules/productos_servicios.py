from app.db import Database


class ProductosServiciosModule:
    def __init__(self):
        self.db = Database()

    def listar(self):
        return self.db.get_productos_servicios()

    def obtener(self, id_producto):
        return self.db.get_producto_servicio(id_producto)

    def crear(self, codigo, descripcion, precio, iva=21, unidad="unidad",
              stock=0, rubro=""):
        self.db.insertar_producto_servicio(
            codigo,
            descripcion,
            precio,
            iva,
            unidad,
            stock,
            rubro
        )

    def editar(self, id_producto, codigo, descripcion, precio, iva=21,
               unidad="unidad", stock=0, rubro=""):
        self.db.actualizar_producto_servicio(
            id_producto,
            codigo,
            descripcion,
            precio,
            iva,
            unidad,
            stock,
            rubro
        )

    def eliminar(self, id_producto):
        self.db.eliminar_producto_servicio(id_producto)

    def cerrar(self):
        self.db.cerrar()
