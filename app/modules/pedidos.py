from app.db import Database


class PedidosModule:
    def __init__(self):
        self.db = Database()

    def listar(self):
        return self.db.get_pedidos()

    def listar_clientes(self):
        return self.db.get_clientes()

    def crear(self, id_cliente, tipo_trabajo, descripcion, precio_costo,
              precio_final, sena, fecha, fecha_ingreso, estado="Pendiente"):
        self.db.insertar_pedido(
            id_cliente, tipo_trabajo, descripcion,
            precio_costo, precio_final, sena, fecha, fecha_ingreso, estado
        )

    def crear_varios(self, id_cliente, fecha, fecha_ingreso, estado, trabajos):
        self.db.insertar_pedidos_varios(id_cliente, fecha, fecha_ingreso, estado, trabajos)

    def editar(self, id_pedido, id_cliente, tipo_trabajo, descripcion,
               precio_costo, precio_final, sena, fecha, fecha_ingreso, estado):
        self.db.actualizar_pedido(
            id_pedido, id_cliente, tipo_trabajo, descripcion,
            precio_costo, precio_final, sena, fecha, fecha_ingreso, estado
        )

    def eliminar(self, id_pedido):
        self.db.eliminar_pedido(id_pedido)

    def subtotales_por_estado(self):
        return self.db.get_subtotales_saldo_por_estado()

    def cerrar(self):
        self.db.cerrar()