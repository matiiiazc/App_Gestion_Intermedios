from app.db import Database


class PedidosModule:
    def __init__(self):
        self.db = Database()

    def listar(self):
        return self.db.get_pedidos()

    def listar_clientes(self):
        return self.db.get_clientes()

    def crear(self, id_cliente, tipo_trabajo, descripcion, precio_costo,
              precio_final, sena, fecha, estado="Pendiente"):
        self.db.insertar_pedido(
            id_cliente, tipo_trabajo, descripcion,
            precio_costo, precio_final, sena, fecha, estado
        )

    def crear_varios(self, id_cliente, fecha, estado, trabajos):
        self.db.insertar_pedidos_varios(id_cliente, fecha, estado, trabajos)

    def editar(self, id_pedido, id_cliente, tipo_trabajo, descripcion,
               precio_costo, precio_final, sena, fecha, estado):
        self.db.actualizar_pedido(
            id_pedido, id_cliente, tipo_trabajo, descripcion,
            precio_costo, precio_final, sena, fecha, estado
        )

    def eliminar(self, id_pedido):
        self.db.eliminar_pedido(id_pedido)

    def cerrar(self):
        self.db.cerrar()
