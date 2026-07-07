from app.db import Database


class PresupuestosModule:
    def __init__(self):
        self.db = Database()

    def listar(self):
        return self.db.get_presupuestos()

    def listar_clientes(self):
        return self.db.get_clientes()

    def crear(self, id_cliente, tipo_trabajo, descripcion, fecha_ingreso,
              fecha_inicio, fecha_expiracion, total):
        self.db.insertar_presupuesto(
            id_cliente,
            tipo_trabajo,
            descripcion,
            fecha_ingreso,
            fecha_inicio,
            fecha_expiracion,
            total
        )

    def editar(self, id_presupuesto, id_cliente, tipo_trabajo, descripcion,
               fecha_ingreso, fecha_inicio, fecha_expiracion, total):
        self.db.actualizar_presupuesto(
            id_presupuesto,
            id_cliente,
            tipo_trabajo,
            descripcion,
            fecha_ingreso,
            fecha_inicio,
            fecha_expiracion,
            total
        )

    def eliminar(self, id_presupuesto):
        self.db.eliminar_presupuesto(id_presupuesto)

    def cerrar(self):
        self.db.cerrar()

    def aceptar(self, id_presupuesto):
        return self.db.aceptar_presupuesto(id_presupuesto)