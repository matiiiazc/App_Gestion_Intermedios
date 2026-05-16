import sqlite3
from pathlib import Path


class Database:
    def __init__(self, nombre_db="intermedios.db"):
        ruta = Path(__file__).resolve().parent.parent / "database" / nombre_db

        self.conn = sqlite3.connect(ruta)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")

    def cerrar(self):
        self.conn.close()
    #====CLIENTES====

    def get_clientes(self, tipo_cliente="Todos"):
        query = """
            SELECT
                id_cliente,
                tipo_cliente,
                CASE
                    WHEN tipo_cliente = 'Empresa' THEN nombre_empresa
                    ELSE nombre || ' ' || apellido
                END AS cliente,
                nombre,
                apellido,
                nombre_empresa,
                telefono,
                direccion,
                cuil,
                dni,
                condicion_iva,
                localidad,
                provincia,
                email,
                cantidad_trabajos
            FROM clientes
        """

        params = []

        if tipo_cliente != "Todos":
            query += " WHERE tipo_cliente = ?"
            params.append(tipo_cliente)

        query += " ORDER BY tipo_cliente, cliente"

        return self.conn.execute(query, params).fetchall()

    def get_cliente(self, id_cliente):
        return self.conn.execute(
            "SELECT * FROM clientes WHERE id_cliente = ?",
            (id_cliente,)
        ).fetchone()

    def insertar_cliente_particular(self, nombre, apellido, telefono="", cuil="",
                                    dni="", condicion_iva="", direccion="",
                                    localidad="", provincia="", email=""):
        self.conn.execute(
            """INSERT INTO clientes
               (tipo_cliente, nombre, apellido, nombre_empresa, telefono,
                direccion, cuil, dni, condicion_iva, localidad, provincia, email)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "Particular",
                nombre,
                apellido,
                None,
                telefono,
                direccion,
                cuil,
                dni,
                condicion_iva,
                localidad,
                provincia,
                email
            )
        )
        self.conn.commit()

    def insertar_cliente_empresa(self, nombre_empresa, telefono="", direccion="",
                                 cuil="", condicion_iva="", localidad="",
                                 provincia="", email=""):
        self.conn.execute(
            """INSERT INTO clientes
               (tipo_cliente, nombre, apellido, nombre_empresa, telefono,
                direccion, cuil, dni, condicion_iva, localidad, provincia, email)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "Empresa",
                "",
                "",
                nombre_empresa,
                telefono,
                direccion,
                cuil,
                "",
                condicion_iva,
                localidad,
                provincia,
                email
            )
        )
        self.conn.commit()

    def actualizar_cliente_particular(self, id_cliente, nombre, apellido,
                                      telefono="", cuil="", dni="",
                                      condicion_iva="", direccion="",
                                      localidad="", provincia="", email=""):
        self.conn.execute(
            """UPDATE clientes
               SET tipo_cliente = ?,
                   nombre = ?,
                   apellido = ?,
                   nombre_empresa = ?,
                   telefono = ?,
                   direccion = ?,
                   cuil = ?,
                   dni = ?,
                   condicion_iva = ?,
                   localidad = ?,
                   provincia = ?,
                   email = ?
               WHERE id_cliente = ?""",
            (
                "Particular",
                nombre,
                apellido,
                None,
                telefono,
                direccion,
                cuil,
                dni,
                condicion_iva,
                localidad,
                provincia,
                email,
                id_cliente
            )
        )
        self.conn.commit()

    def actualizar_cliente_empresa(self, id_cliente, nombre_empresa,
                                   telefono="", direccion="", cuil="",
                                   condicion_iva="", localidad="",
                                   provincia="", email=""):
        self.conn.execute(
            """UPDATE clientes
               SET tipo_cliente = ?,
                   nombre = ?,
                   apellido = ?,
                   nombre_empresa = ?,
                   telefono = ?,
                   direccion = ?,
                   cuil = ?,
                   dni = ?,
                   condicion_iva = ?,
                   localidad = ?,
                   provincia = ?,
                   email = ?
               WHERE id_cliente = ?""",
            (
                "Empresa",
                "",
                "",
                nombre_empresa,
                telefono,
                direccion,
                cuil,
                "",
                condicion_iva,
                localidad,
                provincia,
                email,
                id_cliente
            )
        )
        self.conn.commit()

    def cliente_tiene_datos_facturacion(self, id_cliente):
        cliente = self.get_cliente(id_cliente)

        if not cliente:
            return False

        campos_obligatorios = [
            cliente["cuil"],
            cliente["condicion_iva"],
            cliente["direccion"],
            cliente["localidad"],
            cliente["provincia"],
        ]

        return all(campo and str(campo).strip() for campo in campos_obligatorios)

    def eliminar_cliente(self, id_cliente):
        self.conn.execute(
            "DELETE FROM clientes WHERE id_cliente = ?",
            (id_cliente,)
        )
        self.conn.commit()

    def get_pedidos_cliente(self, id_cliente):
        return self.conn.execute(
            """SELECT *
               FROM pedidos
               WHERE id_cliente = ?
               ORDER BY fecha DESC, id_pedido DESC""",
            (id_cliente,)
        ).fetchall()



    # ====PEDIDOS====
    def get_pedidos(self):
        return self.conn.execute("""
            SELECT
                p.*,
                CASE
                    WHEN c.tipo_cliente = 'Empresa' THEN c.nombre_empresa
                    ELSE c.nombre || ' ' || c.apellido
                END AS cliente
            FROM pedidos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
            ORDER BY p.id_pedido DESC
        """).fetchall()

    def insertar_pedido(self, id_cliente, tipo_trabajo, descripcion,
                        precio_costo, precio_final, sena, fecha, estado="Pendiente"):
        self.conn.execute(
            """INSERT INTO pedidos
               (id_cliente, tipo_trabajo, descripcion, precio_costo,
                precio_final, sena, fecha, estado)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (id_cliente, tipo_trabajo, descripcion, precio_costo,
             precio_final, sena, fecha, estado)
        )

        self.conn.execute(
            """UPDATE clientes
               SET cantidad_trabajos = cantidad_trabajos + 1
               WHERE id_cliente = ?""",
            (id_cliente,)
        )

        self.conn.commit()

    def insertar_pedidos_varios(self, id_cliente, fecha, estado, trabajos):
        for trabajo in trabajos:
            self.conn.execute(
                """INSERT INTO pedidos
                   (id_cliente, tipo_trabajo, descripcion, precio_costo,
                    precio_final, sena, fecha, estado)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    id_cliente,
                    trabajo["tipo_trabajo"],
                    trabajo["descripcion"],
                    trabajo["precio_costo"],
                    trabajo["precio_final"],
                    trabajo["sena"],
                    fecha,
                    estado
                )
            )

        self.conn.execute(
            """UPDATE clientes
               SET cantidad_trabajos = cantidad_trabajos + ?
               WHERE id_cliente = ?""",
            (len(trabajos), id_cliente)
        )

        self.conn.commit()

    def actualizar_pedido(self, id_pedido, id_cliente, tipo_trabajo, descripcion,
                          precio_costo, precio_final, sena, fecha, estado):
        self.conn.execute(
            """UPDATE pedidos
               SET id_cliente = ?,
                   tipo_trabajo = ?,
                   descripcion = ?,
                   precio_costo = ?,
                   precio_final = ?,
                   sena = ?,
                   fecha = ?,
                   estado = ?
               WHERE id_pedido = ?""",
            (
                id_cliente,
                tipo_trabajo,
                descripcion,
                precio_costo,
                precio_final,
                sena,
                fecha,
                estado,
                id_pedido
            )
        )
        self.conn.commit()

    def eliminar_pedido(self, id_pedido):
        pedido = self.conn.execute(
            "SELECT id_cliente FROM pedidos WHERE id_pedido = ?",
            (id_pedido,)
        ).fetchone()

        self.conn.execute(
            "DELETE FROM pedidos WHERE id_pedido = ?",
            (id_pedido,)
        )

        if pedido:
            self.conn.execute(
                """UPDATE clientes
                   SET cantidad_trabajos = CASE
                       WHEN cantidad_trabajos > 0 THEN cantidad_trabajos - 1
                       ELSE 0
                   END
                   WHERE id_cliente = ?""",
                (pedido["id_cliente"],)
            )

        self.conn.commit()



    # ====PRESUPUESTOS====

    def get_presupuestos(self):
        return self.conn.execute("""
            SELECT
                p.*,
                CASE
                    WHEN c.tipo_cliente = 'Empresa' THEN c.nombre_empresa
                    ELSE c.nombre || ' ' || c.apellido
                END AS cliente
            FROM presupuestos p
            JOIN clientes c ON p.id_cliente = c.id_cliente
            ORDER BY p.id_presupuesto DESC
        """).fetchall()

    def insertar_presupuesto(self, id_cliente, tipo_trabajo, fecha_ingreso,
                             fecha_inicio, fecha_expiracion, total):
        self.conn.execute(
            """INSERT INTO presupuestos
               (id_cliente, tipo_trabajo, fecha_ingreso,
                fecha_inicio, fecha_expiracion, total)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                id_cliente,
                tipo_trabajo,
                fecha_ingreso,
                fecha_inicio,
                fecha_expiracion,
                total
            )
        )
        self.conn.commit()

    def actualizar_presupuesto(self, id_presupuesto, id_cliente, tipo_trabajo,
                               fecha_ingreso, fecha_inicio, fecha_expiracion, total):
        self.conn.execute(
            """UPDATE presupuestos
               SET id_cliente = ?,
                   tipo_trabajo = ?,
                   fecha_ingreso = ?,
                   fecha_inicio = ?,
                   fecha_expiracion = ?,
                   total = ?
               WHERE id_presupuesto = ?""",
            (
                id_cliente,
                tipo_trabajo,
                fecha_ingreso,
                fecha_inicio,
                fecha_expiracion,
                total,
                id_presupuesto
            )
        )
        self.conn.commit()

    def eliminar_presupuesto(self, id_presupuesto):
        self.conn.execute(
            "DELETE FROM presupuestos WHERE id_presupuesto = ?",
            (id_presupuesto,)
        )
        self.conn.commit()

    def aceptar_presupuesto(self, id_presupuesto):
        presupuesto = self.conn.execute(
            """SELECT *
               FROM presupuestos
               WHERE id_presupuesto = ?""",
            (id_presupuesto,)
        ).fetchone()

        if not presupuesto:
            return False

        if "estado" in presupuesto.keys() and presupuesto["estado"] == "Aceptado":
            return False

        fecha_pedido = presupuesto["fecha_inicio"] or presupuesto["fecha_ingreso"]

        self.conn.execute(
            """INSERT INTO pedidos
               (id_cliente, tipo_trabajo, descripcion, precio_costo,
                precio_final, sena, fecha, estado)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                presupuesto["id_cliente"],
                presupuesto["tipo_trabajo"],
                "Generado desde presupuesto",
                0,
                presupuesto["total"],
                0,
                fecha_pedido,
                "Pendiente"
            )
        )

        self.conn.execute(
            """UPDATE presupuestos
               SET estado = 'Aceptado'
               WHERE id_presupuesto = ?""",
            (id_presupuesto,)
        )

        self.conn.execute(
            """UPDATE clientes
               SET cantidad_trabajos = cantidad_trabajos + 1
               WHERE id_cliente = ?""",
            (presupuesto["id_cliente"],)
        )

        self.conn.commit()
        return True


    # ====PRODUCTOS SERVICIOS====

    def get_productos_servicios(self):
        return self.conn.execute("""
            SELECT *
            FROM productos_servicios
            ORDER BY rubro, descripcion
        """).fetchall()

    def get_producto_servicio(self, id_producto):
        return self.conn.execute(
            """SELECT *
               FROM productos_servicios
               WHERE id_producto = ?""",
            (id_producto,)
        ).fetchone()

    def insertar_producto_servicio(self, codigo, descripcion, precio,
                                   iva=21, unidad="unidad", stock=0, rubro=""):
        self.conn.execute(
            """INSERT INTO productos_servicios
               (codigo, descripcion, precio, iva, unidad, stock, rubro)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                codigo,
                descripcion,
                precio,
                iva,
                unidad,
                stock,
                rubro
            )
        )
        self.conn.commit()

    def actualizar_producto_servicio(self, id_producto, codigo, descripcion,
                                     precio, iva=21, unidad="unidad",
                                     stock=0, rubro=""):
        self.conn.execute(
            """UPDATE productos_servicios
               SET codigo = ?,
                   descripcion = ?,
                   precio = ?,
                   iva = ?,
                   unidad = ?,
                   stock = ?,
                   rubro = ?
               WHERE id_producto = ?""",
            (
                codigo,
                descripcion,
                precio,
                iva,
                unidad,
                stock,
                rubro,
                id_producto
            )
        )
        self.conn.commit()

    def eliminar_producto_servicio(self, id_producto):
        self.conn.execute(
            "DELETE FROM productos_servicios WHERE id_producto = ?",
            (id_producto,)
        )
        self.conn.commit()

    #==== EMISOR ====
    def get_emisor(self):
        return self.conn.execute("""
            SELECT *
            FROM emisor
            ORDER BY id_emisor
            LIMIT 1
        """).fetchone()

    def guardar_emisor(self, datos):
        emisor = self.get_emisor()

        if emisor:
            self.conn.execute(
                """UPDATE emisor
                   SET razon_social = ?,
                       nombre_fantasia = ?,
                       cuit = ?,
                       condicion_iva = ?,
                       domicilio = ?,
                       inicio_actividades = ?,
                       punto_venta = ?,
                       ingresos_brutos = ?,
                       certificado_mipyme = ?,
                       email = ?,
                       telefono = ?
                   WHERE id_emisor = ?""",
                (
                    datos["razon_social"],
                    datos["nombre_fantasia"],
                    datos["cuit"],
                    datos["condicion_iva"],
                    datos["domicilio"],
                    datos["inicio_actividades"],
                    datos["punto_venta"],
                    datos["ingresos_brutos"],
                    datos["certificado_mipyme"],
                    datos["email"],
                    datos["telefono"],
                    emisor["id_emisor"]
                )
            )
        else:
            self.conn.execute(
                """INSERT INTO emisor
                   (razon_social, nombre_fantasia, cuit, condicion_iva,
                    domicilio, inicio_actividades, punto_venta,
                    ingresos_brutos, certificado_mipyme, email, telefono)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    datos["razon_social"],
                    datos["nombre_fantasia"],
                    datos["cuit"],
                    datos["condicion_iva"],
                    datos["domicilio"],
                    datos["inicio_actividades"],
                    datos["punto_venta"],
                    datos["ingresos_brutos"],
                    datos["certificado_mipyme"],
                    datos["email"],
                    datos["telefono"]
                )
            )

        self.conn.commit()

    #====FACTURAS====
    def get_facturas(self):
        return self.conn.execute("""
            SELECT
                f.*,
                CASE
                    WHEN c.tipo_cliente = 'Empresa' THEN c.nombre_empresa
                    ELSE c.nombre || ' ' || c.apellido
                END AS cliente
            FROM facturas f
            JOIN clientes c ON f.cliente_id = c.id_cliente
            ORDER BY f.fecha DESC, f.id_factura DESC
        """).fetchall()

    def get_factura(self, id_factura):
        return self.conn.execute(
            "SELECT * FROM facturas WHERE id_factura = ?",
            (id_factura,)
        ).fetchone()

    def get_factura_detalles(self, id_factura):
        return self.conn.execute("""
            SELECT *
            FROM factura_detalles
            WHERE factura_id = ?
            ORDER BY id_detalle
        """, (id_factura,)).fetchall()

    def insertar_factura_con_detalles(self, datos, detalles):
        cursor = self.conn.execute(
            """INSERT INTO facturas
               (tipo_comprobante, punto_venta, numero, fecha, cliente_id,
                subtotal, iva, total, forma_pago, observaciones,
                cae, vencimiento_cae, estado_arca)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                datos["tipo_comprobante"],
                datos["punto_venta"],
                datos["numero"],
                datos["fecha"],
                datos["cliente_id"],
                datos["subtotal"],
                datos["iva"],
                datos["total"],
                datos["forma_pago"],
                datos["observaciones"],
                datos["cae"],
                datos["vencimiento_cae"],
                datos["estado_arca"]
            )
        )

        id_factura = cursor.lastrowid

        for detalle in detalles:
            self.conn.execute(
                """INSERT INTO factura_detalles
                   (factura_id, producto_id, descripcion, cantidad,
                    precio_unitario, iva, subtotal)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    id_factura,
                    detalle["producto_id"],
                    detalle["descripcion"],
                    detalle["cantidad"],
                    detalle["precio_unitario"],
                    detalle["iva"],
                    detalle["subtotal"]
                )
            )

        self.conn.commit()

    def actualizar_factura_arca(self, id_factura, numero, cae, vencimiento_cae, estado_arca):
        """Actualiza los campos de ARCA en una factura existente."""
        self.conn.execute(
            """UPDATE facturas
               SET numero = ?,
                   cae = ?,
                   vencimiento_cae = ?,
                   estado_arca = ?
               WHERE id_factura = ?""",
            (numero, cae, vencimiento_cae, estado_arca, id_factura)
        )
        self.conn.commit()

    def eliminar_factura(self, id_factura):
        self.conn.execute(
            "DELETE FROM facturas WHERE id_factura = ?",
            (id_factura,)
        )
        self.conn.commit()