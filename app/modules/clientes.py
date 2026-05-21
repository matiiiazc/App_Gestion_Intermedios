from app.db import Database


class ClientesModule:
    def __init__(self):
        self.db = Database()

    def listar(self, tipo_cliente="Todos"):
        return self.db.get_clientes(tipo_cliente)

    def obtener(self, id_cliente):
        return self.db.get_cliente(id_cliente)

    def crear_particular(self, nombre, apellido,
                         telefono="", direccion="", email=""):
        self.db.insertar_cliente_particular(
            nombre, apellido, telefono, direccion, email
        )

    def crear_empresa(self, nombre_empresa,
                      telefono="", direccion="", email=""):
        self.db.insertar_cliente_empresa(
            nombre_empresa, telefono, direccion, email
        )

    def editar_particular(self, id_cliente, nombre, apellido,
                          telefono="", direccion="", email=""):
        self.db.actualizar_cliente_particular(
            id_cliente, nombre, apellido, telefono, direccion, email
        )

    def editar_empresa(self, id_cliente, nombre_empresa,
                       telefono="", direccion="", email=""):
        self.db.actualizar_cliente_empresa(
            id_cliente, nombre_empresa, telefono, direccion, email
        )

    def eliminar(self, id_cliente):
        self.db.eliminar_cliente(id_cliente)

    def trabajos_cliente(self, id_cliente):
        return self.db.get_pedidos_cliente(id_cliente)

    def cerrar(self):
        self.db.cerrar()