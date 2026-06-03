from database.connection import Database
from utils.permissions import require_permission
from utils.validaciones import as_decimal, as_int, required


class ProductoController:
    def __init__(self, db: Database | None = None):
        self.db = db or Database()

    def list_categories(self) -> list[str]:
        rows = self.db.fetch_all(
            "SELECT nombre FROM categorias WHERE activo = 1 ORDER BY nombre"
        )
        return [row["nombre"] for row in rows]

    def list_category_rows(self) -> list[dict]:
        return self.db.fetch_all(
            """
            SELECT c.id, c.nombre, c.descripcion, c.activo,
                   COUNT(s.id) AS subcategorias
            FROM categorias c
            LEFT JOIN subcategorias s ON s.categoria_id = c.id AND s.activa = 1
            GROUP BY c.id, c.nombre, c.descripcion, c.activo
            ORDER BY c.nombre
            """
        )

    def list_subcategories(self, category_name: str | None = None) -> list[str]:
        params = []
        where = "WHERE s.activa = 1"
        if category_name:
            where += " AND c.nombre = %s"
            params.append(category_name)
        rows = self.db.fetch_all(
            f"""
            SELECT s.nombre
            FROM subcategorias s
            JOIN categorias c ON c.id = s.categoria_id
            {where}
            ORDER BY s.nombre
            """,
            tuple(params),
        )
        return [row["nombre"] for row in rows]

    def list_subcategory_rows(self, category_name: str | None = None) -> list[dict]:
        params = []
        where = "WHERE s.activa = 1"
        if category_name:
            where += " AND c.nombre = %s"
            params.append(category_name)
        return self.db.fetch_all(
            f"""
            SELECT s.id, s.nombre, c.nombre AS categoria, s.activa
            FROM subcategorias s
            JOIN categorias c ON c.id = s.categoria_id
            {where}
            ORDER BY c.nombre, s.nombre
            """,
            tuple(params),
        )

    def list_products(self, search: str | None = None) -> list[dict]:
        params: list = []
        where = "WHERE p.activo = 1"
        if search:
            where += " AND (p.codigo LIKE %s OR p.nombre LIKE %s OR c.nombre LIKE %s)"
            like = f"%{search}%"
            params.extend([like, like, like])

        return self.db.fetch_all(
            f"""
            SELECT p.id, p.codigo, p.nombre, p.marca, c.nombre AS categoria,
                   p.subcategoria, p.presentacion, p.precio_venta,
                   p.precio_compra, i.stock_actual, i.stock_minimo,
                   i.merma, i.ubicacion
            FROM productos p
            JOIN categorias c ON c.id = p.categoria_id
            JOIN inventario i ON i.producto_id = p.id
            {where}
            ORDER BY c.nombre, p.nombre
            """,
            tuple(params),
        )

    def save_product(self, data: dict, user: dict) -> int:
        require_permission(user, "products_write")
        codigo = required(data.get("codigo"), "codigo").upper()
        nombre = required(data.get("nombre"), "nombre")
        marca = required(data.get("marca"), "marca")
        categoria = required(data.get("categoria"), "categoria")
        subcategoria = required(data.get("subcategoria"), "subcategoria")
        presentacion = required(data.get("presentacion"), "presentacion")
        precio_venta = as_decimal(data.get("precio_venta"), "precio de venta")
        precio_compra = as_decimal(data.get("precio_compra") or "0", "precio de compra")
        stock_actual = as_int(data.get("stock_actual") or "0", "stock")
        stock_minimo = as_int(data.get("stock_minimo") or "5", "stock minimo")

        with self.db.cursor(commit=True) as cur:
            categoria_id = self._ensure_category(cur, categoria)
            self._ensure_subcategory(cur, categoria_id, subcategoria)
            cur.execute("SELECT id FROM productos WHERE codigo = %s", (codigo,))
            existing = cur.fetchone()
            if existing:
                producto_id = existing["id"]
                cur.execute(
                    """
                    UPDATE productos
                    SET nombre=%s, marca=%s, categoria_id=%s, subcategoria=%s,
                        presentacion=%s, precio_venta=%s, precio_compra=%s,
                        activo=1
                    WHERE id=%s
                    """,
                    (
                        nombre,
                        marca,
                        categoria_id,
                        subcategoria,
                        presentacion,
                        precio_venta,
                        precio_compra,
                        producto_id,
                    ),
                )
                cur.execute(
                    """
                    UPDATE inventario
                    SET stock_actual=%s, stock_minimo=%s
                    WHERE producto_id=%s
                    """,
                    (stock_actual, stock_minimo, producto_id),
                )
                action = "Actualizacion de producto"
            else:
                cur.execute(
                    """
                    INSERT INTO productos
                        (codigo, nombre, marca, categoria_id, subcategoria,
                         presentacion, precio_venta, precio_compra)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        codigo,
                        nombre,
                        marca,
                        categoria_id,
                        subcategoria,
                        presentacion,
                        precio_venta,
                        precio_compra,
                    ),
                )
                producto_id = cur.lastrowid
                cur.execute(
                    """
                    INSERT INTO inventario
                        (producto_id, stock_actual, stock_minimo, merma)
                    VALUES (%s, %s, %s, 0)
                    """,
                    (producto_id, stock_actual, stock_minimo),
                )
                action = "Alta de producto"

            self._log(cur, user["id"], "productos", action, f"{codigo} - {nombre}")
            return producto_id

    def adjust_stock(self, producto_id: int, cantidad: int, user: dict, motivo: str):
        require_permission(user, "inventory_write")
        with self.db.cursor(commit=True) as cur:
            cur.execute(
                """
                UPDATE inventario
                SET stock_actual = GREATEST(stock_actual + %s, 0)
                WHERE producto_id = %s
                """,
                (cantidad, producto_id),
            )
            self._log(
                cur,
                user["id"],
                "inventario",
                "Ajuste de stock",
                f"Producto {producto_id}: {cantidad:+d}. Motivo: {motivo}",
            )

    def save_category(self, name: str, description: str, user: dict) -> int:
        require_permission(user, "categories_manage")
        name = required(name, "categoria")
        with self.db.cursor(commit=True) as cur:
            cur.execute("SELECT id FROM categorias WHERE nombre = %s", (name,))
            row = cur.fetchone()
            if row:
                cur.execute(
                    "UPDATE categorias SET descripcion=%s, activo=1 WHERE id=%s",
                    (description, row["id"]),
                )
                category_id = row["id"]
                action = "Actualizacion de categoria"
            else:
                cur.execute(
                    "INSERT INTO categorias (nombre, descripcion) VALUES (%s, %s)",
                    (name, description),
                )
                category_id = cur.lastrowid
                action = "Alta de categoria"
            self._log(cur, user["id"], "categorias", action, name)
            return category_id

    def save_subcategory(self, category_name: str, subcategory_name: str, user: dict) -> int:
        require_permission(user, "categories_manage")
        category_name = required(category_name, "categoria")
        subcategory_name = required(subcategory_name, "subcategoria")
        with self.db.cursor(commit=True) as cur:
            category_id = self._ensure_category(cur, category_name)
            subcategory_id = self._ensure_subcategory(cur, category_id, subcategory_name)
            self._log(
                cur,
                user["id"],
                "categorias",
                "Alta de subcategoria",
                f"{category_name} / {subcategory_name}",
            )
            return subcategory_id

    def _ensure_category(self, cur, name: str) -> int:
        cur.execute("SELECT id FROM categorias WHERE nombre = %s", (name,))
        row = cur.fetchone()
        if row:
            return row["id"]
        cur.execute(
            "INSERT INTO categorias (nombre, descripcion) VALUES (%s, %s)",
            (name, "Categoria creada desde el sistema"),
        )
        return cur.lastrowid

    def _ensure_subcategory(self, cur, categoria_id: int, name: str) -> int:
        cur.execute(
            "SELECT id FROM subcategorias WHERE categoria_id = %s AND nombre = %s",
            (categoria_id, name),
        )
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE subcategorias SET activa = 1 WHERE id = %s", (row["id"],))
            return row["id"]
        cur.execute(
            "INSERT INTO subcategorias (categoria_id, nombre) VALUES (%s, %s)",
            (categoria_id, name),
        )
        return cur.lastrowid

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
