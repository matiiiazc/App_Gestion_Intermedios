from app.db import Database


CATEGORIAS = [
    "Gigantografía",
    "Polifan",
    "Vinilos",
    "DFT´S",
    "Indumentaria",
    "Otros",
]


class GastosModule:
    def __init__(self):
        self.db = Database()

    def listar(self):
        return self.db.get_gastos()

    def get_gasto(self, id_gasto):
        return self.db.get_gasto(id_gasto)

    def listar_por_proveedor(self, proveedor: str):
        return self.db.get_gastos_por_proveedor(proveedor)

    def get_proveedores(self) -> list:
        return self.db.get_proveedores_gastos()

    def get_totales_por_proveedor(self) -> list:
        return self.db.get_totales_gastos_por_proveedor()

    def crear(self, producto, proveedor, descripcion, categoria, costo, fecha=None):
        self.db.insertar_gasto(producto, proveedor, descripcion, categoria, costo, fecha)

    def editar(self, id_gasto, producto, proveedor, descripcion, categoria, costo, fecha):
        self.db.actualizar_gasto(id_gasto, producto, proveedor, descripcion, categoria, costo, fecha)

    def eliminar(self, id_gasto):
        self.db.eliminar_gasto(id_gasto)

    def cerrar(self):
        self.db.cerrar()