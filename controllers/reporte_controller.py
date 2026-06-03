from database.connection import Database
from utils.permissions import require_permission


class ReporteController:
    def __init__(self, db: Database | None = None):
        self.db = db or Database()

    def get_dashboard_summary(self, user: dict | None = None) -> dict:
        return {
            "productos": self._scalar("SELECT COUNT(*) total FROM productos WHERE activo = 1"),
            "stock_bajo": self._scalar(
                """
                SELECT COUNT(*) total
                FROM inventario
                WHERE stock_actual <= stock_minimo
                """
            ),
            "ventas_hoy": self._scalar(
                """
                SELECT COALESCE(SUM(total), 0) total
                FROM pedidos_cliente
                WHERE DATE(created_at) = CURDATE()
                  AND estado <> 'CANCELADA'
                """
            ),
            "pedidos_pendientes": self._scalar(
                "SELECT COUNT(*) total FROM pedidos_cliente WHERE estado = 'PENDIENTE'"
            ),
        }

    def list_history(self, user: dict, limit: int = 200) -> list[dict]:
        require_permission(user, "history_full")
        return self.db.fetch_all(
            """
            SELECT h.id, h.created_at, u.username, h.modulo,
                   h.operacion, h.descripcion
            FROM historial_operaciones h
            LEFT JOIN usuarios u ON u.id = h.usuario_id
            ORDER BY h.created_at DESC
            LIMIT %s
            """,
            (limit,),
        )

    def low_stock(self) -> list[dict]:
        return self.db.fetch_all(
            """
            SELECT 
                p.codigo,
                p.nombre,
                c.nombre AS categoria,
                i.stock_actual,
                i.stock_minimo,
                GREATEST(i.stock_minimo - i.stock_actual, 0) AS cantidad_sugerida
            FROM inventario i
            JOIN productos p ON p.id = i.producto_id
            JOIN categorias c ON c.id = p.categoria_id
            WHERE i.stock_actual <= i.stock_minimo
            ORDER BY i.stock_actual ASC
            """
        )

    def sales_by_day(self, days: int = 30) -> list[dict]:
        return self.db.fetch_all(
            """
            SELECT 
                DATE(created_at) AS fecha,
                COUNT(*) AS cantidad_ventas,
                COALESCE(SUM(total), 0) AS total
            FROM ventas
            WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            AND estado <> 'CANCELADA'
            GROUP BY DATE(created_at)
            ORDER BY fecha DESC
            """,
            (days,),
        )

    def _scalar(self, query: str, params: tuple | None = None):
        row = self.db.fetch_one(query, params)
        return row["total"] if row else 0
