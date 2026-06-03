from database.connection import Database
from utils.permissions import require_permission


CLIENT_MODALITIES = {
    "Recoger en tienda": "Recoger en tienda",
    "Pedido a domicilio": "Entrega a domicilio",
}


class PedidoController:
    def __init__(self, db: Database | None = None):
        self.db = db or Database()

    def list_modalidades(self) -> list[str]:
        rows = self.db.fetch_all(
            "SELECT nombre FROM modalidades_entrega WHERE activa = 1 ORDER BY id"
        )
        return [row["nombre"] for row in rows]

    def list_client_modalidades(self) -> list[str]:
        return list(CLIENT_MODALITIES.keys())

    def list_formas_pago(self) -> list[str]:
        rows = self.db.fetch_all(
            "SELECT nombre FROM formas_pago WHERE activa = 1 ORDER BY id"
        )
        names = []
        for row in rows:
            name = self.display_payment(row["nombre"])
            if name not in names:
                names.append(name)
        return names

    def create_order(
        self,
        cliente,
        cart_items: list[dict],
        modalidad: str,
        forma_pago: str,
        direccion: str | None = None,
    ) -> int:
        if isinstance(cliente, dict):
            require_permission(cliente, "client_orders")
            cliente_id = cliente["id"]
        else:
            cliente_id = cliente
        if not cart_items:
            raise ValueError("El carrito esta vacio.")
        modalidad_db = self.normalize_modalidad(modalidad)
        if modalidad == "Pedido a domicilio" and not (direccion or "").strip():
            raise ValueError("Ingresa una direccion para pedido a domicilio.")
        if modalidad == "Recoger en tienda":
            direccion = None

        subtotal = sum(float(item["precio_venta"]) * int(item["cantidad"]) for item in cart_items)

        with self.db.cursor(commit=True) as cur:
            modalidad_id = self._id_by_name(cur, "modalidades_entrega", modalidad_db)
            forma_pago_id = self._payment_id(cur, forma_pago)
            cur.execute(
                """
                INSERT INTO pedidos_cliente
                    (cliente_id, modalidad_entrega_id, forma_pago_id,
                     direccion_entrega, subtotal, total)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (cliente_id, modalidad_id, forma_pago_id, direccion, subtotal, subtotal),
            )
            pedido_id = cur.lastrowid
            for item in cart_items:
                cantidad = int(item["cantidad"])
                precio = float(item["precio_venta"])
                cur.execute(
                    """
                    INSERT INTO detalle_pedido
                        (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (pedido_id, item["id"], cantidad, precio, cantidad * precio),
                )
            self._log(
                cur,
                cliente_id,
                "cliente",
                "Pedido registrado",
                f"Pedido {pedido_id} por ${subtotal:.2f}",
            )
            return pedido_id

    def list_orders(self, cliente_id: int | None = None) -> list[dict]:
        params = []
        where = ""
        if cliente_id:
            where = "WHERE p.cliente_id = %s"
            params.append(cliente_id)
        return self.db.fetch_all(
            f"""
            SELECT p.id, p.created_at, u.username AS cliente,
                   me.nombre AS modalidad,
                   CASE WHEN fp.nombre = 'Efectivo en tienda' THEN 'Efectivo' ELSE fp.nombre END AS forma_pago,
                   p.estado, p.total, p.direccion_entrega
            FROM pedidos_cliente p
            JOIN usuarios u ON u.id = p.cliente_id
            JOIN modalidades_entrega me ON me.id = p.modalidad_entrega_id
            JOIN formas_pago fp ON fp.id = p.forma_pago_id
            {where}
            ORDER BY p.created_at DESC
            """,
            tuple(params),
        )

    def get_order_details(self, pedido_id: int, cliente_id: int | None = None) -> list[dict]:
        params: list = [pedido_id]
        owner_filter = ""
        if cliente_id:
            owner_filter = "AND pc.cliente_id = %s"
            params.append(cliente_id)
        return self.db.fetch_all(
            f"""
            SELECT dp.id, prod.codigo, prod.nombre, dp.cantidad,
                   dp.precio_unitario, dp.subtotal
            FROM detalle_pedido dp
            JOIN pedidos_cliente pc ON pc.id = dp.pedido_id
            JOIN productos prod ON prod.id = dp.producto_id
            WHERE dp.pedido_id = %s {owner_filter}
            ORDER BY dp.id
            """,
            tuple(params),
        )

    def cancel_order(self, pedido_id: int, cliente: dict, motivo: str):
        require_permission(cliente, "client_orders")
        allowed_states = {"PENDIENTE", "EN PROCESO"}
        conn = self.db.connect()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                """
                SELECT id, cliente_id, estado
                FROM pedidos_cliente
                WHERE id = %s
                FOR UPDATE
                """,
                (pedido_id,),
            )
            order = cur.fetchone()
            if not order or int(order["cliente_id"]) != int(cliente["id"]):
                raise ValueError("Pedido no encontrado.")
            if order["estado"] not in allowed_states:
                raise ValueError("Este pedido ya no se puede cancelar desde el modulo de cliente.")
            cur.execute(
                "UPDATE pedidos_cliente SET estado = 'CANCELADO' WHERE id = %s",
                (pedido_id,),
            )
            self._log(
                cur,
                cliente["id"],
                "cliente",
                "Pedido cancelado",
                f"Pedido {pedido_id} - Motivo: {motivo}",
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()
            if conn.is_connected():
                conn.close()

    def update_status(self, pedido_id: int, estado: str, user: dict, motivo: str | None = None):
        require_permission(user, "orders_manage")
        with self.db.cursor(commit=True) as cur:
            cur.execute(
                "UPDATE pedidos_cliente SET estado = %s WHERE id = %s",
                (estado, pedido_id),
            )
            detail = f"Pedido {pedido_id}: {estado}"
            if motivo:
                detail = f"{detail} - Motivo: {motivo}"
            self._log(
                cur,
                user["id"],
                "pedidos",
                "Cambio de estado",
                detail,
            )

    @staticmethod
    def normalize_modalidad(modalidad: str) -> str:
        return CLIENT_MODALITIES.get(modalidad, modalidad)

    @staticmethod
    def display_payment(name: str) -> str:
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
    def _id_by_name(cur, table: str, name: str) -> int:
        cur.execute(f"SELECT id FROM {table} WHERE nombre = %s", (name,))
        row = cur.fetchone()
        if not row:
            raise ValueError(f"No existe: {name}")
        return row["id"]

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
