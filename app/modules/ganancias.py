from app.db import Database


class GananciasModule:
    def __init__(self):
        self.db = Database()

    def get_pedidos_periodo(self, fecha_desde: str, fecha_hasta: str):
        return self.db.get_pedidos_por_periodo(fecha_desde, fecha_hasta)

    def get_gastos_periodo(self, fecha_desde: str, fecha_hasta: str):
        return self.db.get_gastos_por_periodo(fecha_desde, fecha_hasta)

    def get_top_proveedores(self, limite: int = 3):
        return self.db.get_top_proveedores(limite)

    def get_top_productos(self, limite: int = 3):
        return self.db.get_top_productos_vendidos(limite)

    def cerrar(self):
        self.db.cerrar()