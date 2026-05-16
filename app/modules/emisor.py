from app.db import Database


class EmisorModule:
    def __init__(self):
        self.db = Database()

    def obtener(self):
        return self.db.get_emisor()

    def guardar(self, datos):
        self.db.guardar_emisor(datos)

    def cerrar(self):
        self.db.cerrar()
