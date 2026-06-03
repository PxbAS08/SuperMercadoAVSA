from datetime import datetime

from database.connection import Database
from utils.comprobante import build_receipt, save_receipt
from utils.permissions import can, require_permission


class VentaController:
    def __init__(self, db: Database | None = None):
        self.db = db or Database()

    def list_formas_pago(self) -> list[str]:
        rows = self.db.fetch_all(
            "SELECT nombre FROM formas_pago WHERE activa = 1 ORDER BY id"
        )
        names = []
        for row in rows:
            name = self._display_payment(row["nombre"])
            if name not in names:
                names.append(name)
        return names

    def list_modalidades(self) -> list[str]:
        rows = self.db.fetch_all(
            "SELECT nombre FROM modalidades_entrega WHERE activa = 1 ORDER BY id"
        )
        return [row["nombre"] for row in rows]

    def register_sale(
        self,
        usuario: dict,
        cart_items: list[dict],
        forma_pago: str,
        modalidad: str,
        cliente_id: int | None = None,
        descuento: float = 0.0,
        monto_saldo: float = 0.0,
        direccion: str | None = None,
        pago_recibido: float | None = None,
    ) -> dict:
        require_permission(usuario, "sales_write")
        if not cart_items:
            raise ValueError("El carrito esta vacio.")

        subtotal = sum(float(item["precio_venta"]) * int(item["cantidad"]) for item in cart_items)
        descuento = max(0.0, float(descuento or 0))
        total = max(0.0, subtotal - descuento)
        is_cash_payment = "efectivo" in (forma_pago or "").lower()
        if pago_recibido is None:
            pago_recibido = total
        pago_recibido = max(0.0, float(pago_recibido or 0))
        if is_cash_payment and pago_recibido < total:
            raise ValueError("El pago recibido no cubre el total de la venta.")
        cambio = max(0.0, pago_recibido - total) if is_cash_payment else 0.0
        monto_efectivo = pago_recibido if is_cash_payment else 0.0
        folio = f"AVS-{datetime.now():%Y%m%d%H%M%S%f}"

        conn = self.db.connect()
        cur = conn.cursor(dictionary=True)
        try:
            forma_pago_id = self._payment_id(cur, forma_pago)
            modalidad_id = self._id_by_name(cur, "modalidades_entrega", modalidad)

            for item in cart_items:
                cur.execute(
                    """
                    SELECT i.stock_actual, p.nombre
                    FROM inventario i
                    JOIN productos p ON p.id = i.producto_id
                    WHERE i.producto_id = %s
                    FOR UPDATE
                    """,
                    (item["id"],),
                )
                stock = cur.fetchone()
                if not stock or stock["stock_actual"] < int(item["cantidad"]):
                    raise ValueError(f"Stock insuficiente para {item['nombre']}.")

            cur.execute(
                """
                INSERT INTO ventas
                    (folio, usuario_id, cliente_id, forma_pago_id,
                     modalidad_entrega_id, subtotal, descuento, total,
                     monto_efectivo, monto_saldo, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'COMPLETADA')
                """,
                (
                    folio,
                    usuario["id"],
                    cliente_id,
                    forma_pago_id,
                    modalidad_id,
                    subtotal,
                    descuento,
                    total,
                    monto_efectivo,
                    monto_saldo,
                ),
            )
            venta_id = cur.lastrowid

            receipt_items = []
            for item in cart_items:
                cantidad = int(item["cantidad"])
                precio = float(item["precio_venta"])
                cur.execute(
                    """
                    INSERT INTO detalle_venta
                        (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (venta_id, item["id"], cantidad, precio, cantidad * precio),
                )
                cur.execute(
                    """
                    UPDATE inventario
                    SET stock_actual = stock_actual - %s
                    WHERE producto_id = %s
                    """,
                    (cantidad, item["id"]),
                )
                receipt_items.append(
                    {
                        "nombre": item["nombre"],
                        "cantidad": cantidad,
                        "precio_unitario": precio,
                    }
                )

            content = build_receipt(
                folio,
                usuario.get("nombre") or usuario.get("username"),
                receipt_items,
                subtotal,
                descuento,
                total,
                forma_pago,
                modalidad,
                direccion=direccion,
                pago_recibido=pago_recibido,
                cambio=cambio,
            )
            path = save_receipt(folio, content)
            cur.execute(
                """
                INSERT INTO comprobantes
                    (venta_id, folio, tipo, ruta_archivo, contenido)
                VALUES (%s, %s, 'VENTA', %s, %s)
                """,
                (venta_id, folio, str(path), content),
            )
            self._log(
                cur,
                usuario["id"],
                "ventas",
                "Venta registrada",
                f"{folio} por ${total:.2f}",
            )
            conn.commit()
            return {
                "venta_id": venta_id,
                "folio": folio,
                "total": total,
                "pago_recibido": pago_recibido,
                "cambio": cambio,
                "comprobante": content,
            }
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            if conn.is_connected():
                conn.close()

    def list_sales(self, limit: int = 100, user: dict | None = None) -> list[dict]:
        params: list = []
        where = ""
        if user and can(user, "sales_read_own") and not can(user, "sales_read_all"):
            where = "WHERE v.usuario_id = %s"
            params.append(user["id"])
        params.append(limit)
        return self.db.fetch_all(
            f"""
            SELECT v.id, v.folio, v.created_at, v.estado, v.subtotal,
                   v.descuento, v.total, v.monto_efectivo, v.monto_saldo,
                   u.username AS usuario, COALESCE(cl.username, 'Mostrador') AS cliente,
                   CASE WHEN fp.nombre = 'Efectivo en tienda' THEN 'Efectivo' ELSE fp.nombre END AS forma_pago,
                   me.nombre AS modalidad
            FROM ventas v
            JOIN usuarios u ON u.id = v.usuario_id
            LEFT JOIN usuarios cl ON cl.id = v.cliente_id
            JOIN formas_pago fp ON fp.id = v.forma_pago_id
            JOIN modalidades_entrega me ON me.id = v.modalidad_entrega_id
            {where}
            ORDER BY v.created_at DESC
            LIMIT %s
            """,
            tuple(params),
        )

    def get_sale(self, venta_id: int) -> dict:
        sale = self.db.fetch_one(
            """
            SELECT v.id, v.folio, v.created_at, v.estado, v.subtotal,
                   v.descuento, v.total, v.monto_efectivo, v.monto_saldo,
                   u.username AS usuario, COALESCE(cl.username, 'Mostrador') AS cliente,
                   CASE WHEN fp.nombre = 'Efectivo en tienda' THEN 'Efectivo' ELSE fp.nombre END AS forma_pago,
                   me.nombre AS modalidad
            FROM ventas v
            JOIN usuarios u ON u.id = v.usuario_id
            LEFT JOIN usuarios cl ON cl.id = v.cliente_id
            JOIN formas_pago fp ON fp.id = v.forma_pago_id
            JOIN modalidades_entrega me ON me.id = v.modalidad_entrega_id
            WHERE v.id = %s
            """,
            (venta_id,),
        )
        if not sale:
            raise ValueError("Venta no encontrada.")
        return sale

    def get_sale_details(self, venta_id: int) -> list[dict]:
        return self.db.fetch_all(
            """
            SELECT d.id, p.codigo, p.nombre, d.cantidad, d.cantidad_devuelta,
                   d.precio_unitario, d.subtotal
            FROM detalle_venta d
            JOIN productos p ON p.id = d.producto_id
            WHERE d.venta_id = %s
            ORDER BY d.id
            """,
            (venta_id,),
        )

    def refund_detail(
        self,
        detalle_id: int,
        user: dict,
        motivo: str,
        tipo_reembolso: str,
    ) -> float:
        require_permission(user, "returns_write")
        conn = self.db.connect()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                """
                SELECT d.*, v.id AS venta_id, v.estado, p.nombre, p.id AS producto_id
                FROM detalle_venta d
                JOIN ventas v ON v.id = d.venta_id
                JOIN productos p ON p.id = d.producto_id
                WHERE d.id = %s
                FOR UPDATE
                """,
                (detalle_id,),
            )
            detail = cur.fetchone()
            if not detail:
                raise ValueError("Detalle no encontrado.")
            if detail["estado"] == "CANCELADA":
                raise ValueError("La venta ya esta cancelada.")
            pending = int(detail["cantidad"]) - int(detail["cantidad_devuelta"])
            if pending <= 0:
                raise ValueError("Este producto ya fue devuelto.")

            monto = pending * float(detail["precio_unitario"])
            damaged = motivo.strip().lower() in {"danado", "dañado", "caducado"}
            if damaged:
                cur.execute(
                    "UPDATE inventario SET merma = merma + %s WHERE producto_id = %s",
                    (pending, detail["producto_id"]),
                )
            else:
                cur.execute(
                    "UPDATE inventario SET stock_actual = stock_actual + %s WHERE producto_id = %s",
                    (pending, detail["producto_id"]),
                )

            cur.execute(
                "UPDATE detalle_venta SET cantidad_devuelta = cantidad WHERE id = %s",
                (detalle_id,),
            )
            cur.execute(
                    """
                    INSERT INTO devoluciones
                        (venta_id, detalle_venta_id, usuario_id, motivo,
                     monto, tipo_reembolso, estado)
                VALUES (%s, %s, %s, %s, %s, %s, 'APLICADA')
                    """,
                (detail["venta_id"], detalle_id, user["id"], motivo, monto, tipo_reembolso),
            )
            cur.execute(
                """
                SELECT COUNT(*) total
                FROM detalle_venta
                WHERE venta_id = %s AND cantidad_devuelta < cantidad
                """,
                (detail["venta_id"],),
            )
            remaining = cur.fetchone()["total"]
            if remaining == 0:
                cur.execute(
                    "UPDATE ventas SET estado = 'DEVUELTA' WHERE id = %s",
                    (detail["venta_id"],),
                )
            self._log(
                cur,
                user["id"],
                "devoluciones",
                "Producto devuelto",
                f"{detail['nombre']} - {motivo} - ${monto:.2f}",
            )
            conn.commit()
            return monto
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            if conn.is_connected():
                conn.close()

    def cancel_sale(self, venta_id: int, user: dict, motivo: str) -> float:
        require_permission(user, "returns_write")
        conn = self.db.connect()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM ventas WHERE id = %s FOR UPDATE", (venta_id,))
            sale = cur.fetchone()
            if not sale:
                raise ValueError("Venta no encontrada.")
            if sale["estado"] == "CANCELADA":
                raise ValueError("La venta ya esta cancelada.")

            cur.execute(
                "SELECT * FROM detalle_venta WHERE venta_id = %s",
                (venta_id,),
            )
            for detail in cur.fetchall():
                restore = int(detail["cantidad"]) - int(detail["cantidad_devuelta"])
                if restore > 0:
                    cur.execute(
                        """
                        UPDATE inventario
                        SET stock_actual = stock_actual + %s
                        WHERE producto_id = %s
                        """,
                        (restore, detail["producto_id"]),
                    )

            cur.execute(
                """
                INSERT INTO cancelaciones
                    (venta_id, usuario_id, motivo, monto)
                VALUES (%s, %s, %s, %s)
                """,
                (venta_id, user["id"], motivo, sale["total"]),
            )
            cur.execute("UPDATE ventas SET estado = 'CANCELADA' WHERE id = %s", (venta_id,))
            self._log(
                cur,
                user["id"],
                "cancelaciones",
                "Venta cancelada",
                f"{sale['folio']} - {motivo}",
            )
            conn.commit()
            return float(sale["total"])
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            if conn.is_connected():
                conn.close()

    @staticmethod
    def _id_by_name(cur, table: str, name: str) -> int:
        cur.execute(f"SELECT id FROM {table} WHERE nombre = %s", (name,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"No existe: {name}")
        return row["id"]

    @staticmethod
    def _display_payment(name: str) -> str:
        return "Efectivo" if name == "Efectivo en tienda" else name

    @staticmethod
    def _payment_id(cur, name: str) -> int:
        aliases = [name]
        if name == "Efectivo":
            aliases.append("Efectivo en tienda")
        for candidate in aliases:
            cur.execute("SELECT id FROM formas_pago WHERE nombre = %s", (candidate,))
            row = cur.fetchone()
            if row:
                return row["id"]
        raise ValueError(f"No existe forma de pago: {name}")

    @staticmethod
    def _log(cur, usuario_id: int, modulo: str, operacion: str, descripcion: str):
        cur.execute(
            """
            INSERT INTO historial_operaciones
                (usuario_id, modulo, operacion, descripcion)
            VALUES (%s, %s, %s, %s)
            """,
            (usuario_id, modulo, operacion, descripcion),
        )
