from app.db import Database


TARIFA_HORA = 5000
EMPLEADOS   = ["Matias", "Gabriel"]


class PagosModule:
    def __init__(self):
        self.db = Database()
        self._init_tablas()

    def _init_tablas(self):
        self.db.conn.executescript("""
            CREATE TABLE IF NOT EXISTS horas_trabajadas (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha     TEXT NOT NULL,
                empleado  TEXT NOT NULL,
                horas     REAL NOT NULL DEFAULT 0,
                tarifa    REAL NOT NULL DEFAULT 5000,
                total     REAL NOT NULL DEFAULT 0,
                creado_en TEXT DEFAULT (datetime('now','localtime'))
            );

            CREATE TABLE IF NOT EXISTS pagos_empleados (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                empleado  TEXT NOT NULL,
                monto     REAL NOT NULL,
                modalidad TEXT NOT NULL,
                fecha     TEXT DEFAULT (date('now','localtime')),
                creado_en TEXT DEFAULT (datetime('now','localtime'))
            );
        """)
        self.db.conn.commit()

    # ── Horas ────────────────────────────────────────────────────────────

    def get_horas_fecha(self, fecha: str) -> dict:
        """Devuelve {empleado: horas} para una fecha dada."""
        rows = self.db.conn.execute(
            "SELECT empleado, horas FROM horas_trabajadas WHERE fecha = ?",
            (fecha,)
        ).fetchall()
        resultado = {e: 0.0 for e in EMPLEADOS}
        for r in rows:
            resultado[r["empleado"]] = r["horas"]
        return resultado

    def guardar_horas(self, fecha: str, horas_por_empleado: dict):
        """Guarda o actualiza las horas de cada empleado para una fecha."""
        for empleado, horas in horas_por_empleado.items():
            horas = float(horas)
            total = round(horas * TARIFA_HORA, 2)
            existente = self.db.conn.execute(
                "SELECT id FROM horas_trabajadas WHERE fecha = ? AND empleado = ?",
                (fecha, empleado)
            ).fetchone()
            if existente:
                self.db.conn.execute(
                    """UPDATE horas_trabajadas
                       SET horas = ?, total = ?, tarifa = ?
                       WHERE fecha = ? AND empleado = ?""",
                    (horas, total, TARIFA_HORA, fecha, empleado)
                )
            else:
                if horas > 0:
                    self.db.conn.execute(
                        """INSERT INTO horas_trabajadas
                           (fecha, empleado, horas, tarifa, total)
                           VALUES (?, ?, ?, ?, ?)""",
                        (fecha, empleado, horas, TARIFA_HORA, total)
                    )
        self.db.conn.commit()

    def get_dias_con_horas(self, anio: int, mes: int) -> list:
        """Devuelve lista de fechas (YYYY-MM-DD) del mes que tienen horas cargadas."""
        patron = f"{anio:04d}-{mes:02d}-%"
        rows = self.db.conn.execute(
            "SELECT DISTINCT fecha FROM horas_trabajadas WHERE fecha LIKE ?",
            (patron,)
        ).fetchall()
        return [r["fecha"] for r in rows]

    # ── Saldos ───────────────────────────────────────────────────────────

    def get_saldo(self, empleado: str) -> dict:
        """Devuelve total devengado, total pagado y saldo pendiente."""
        devengado = self.db.conn.execute(
            "SELECT COALESCE(SUM(total), 0) AS t FROM horas_trabajadas WHERE empleado = ?",
            (empleado,)
        ).fetchone()["t"]

        pagado = self.db.conn.execute(
            "SELECT COALESCE(SUM(monto), 0) AS t FROM pagos_empleados WHERE empleado = ?",
            (empleado,)
        ).fetchone()["t"]

        return {
            "devengado": round(devengado, 2),
            "pagado":    round(pagado, 2),
            "pendiente": round(devengado - pagado, 2),
        }

    # ── Pagos ────────────────────────────────────────────────────────────

    def registrar_pago(self, empleado: str, monto: float, modalidad: str):
        self.db.conn.execute(
            """INSERT INTO pagos_empleados (empleado, monto, modalidad)
               VALUES (?, ?, ?)""",
            (empleado, round(monto, 2), modalidad)
        )
        self.db.conn.commit()

    def get_historial_pagos(self, empleado: str) -> list:
        return self.db.conn.execute(
            """SELECT * FROM pagos_empleados
               WHERE empleado = ?
               ORDER BY id DESC LIMIT 50""",
            (empleado,)
        ).fetchall()

    def get_historial_horas(self, empleado: str) -> list:
        return self.db.conn.execute(
            """SELECT * FROM horas_trabajadas
               WHERE empleado = ?
               ORDER BY fecha DESC LIMIT 50""",
            (empleado,)
        ).fetchall()

    def cerrar(self):
        self.db.cerrar()