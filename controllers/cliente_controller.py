from database.connection import Database
from utils.permissions import require_permission


class ClienteController:
    def __init__(self, db: Database | None = None):
        self.db = db or Database()
        self.ensure_schema()

    def get_profile(self, user_id: int) -> dict:
        self.ensure_schema()
        row = self.db.fetch_one(
            """
            SELECT id, username, nombre, email, telefono, direccion,
                   saldo_electronico
            FROM usuarios
            WHERE id = %s
            """,
            (user_id,),
        )
        if not row:
            raise ValueError("Cliente no encontrado.")
        return row

    def update_profile(self, user: dict, nombre: str, email: str, telefono: str, direccion: str):
        require_permission(user, "client_orders")
        self.ensure_schema()
        with self.db.cursor(commit=True) as cur:
            cur.execute(
                """
                UPDATE usuarios
                SET nombre=%s, email=%s, telefono=%s, direccion=%s
                WHERE id=%s
                """,
                (nombre, email, telefono, direccion, user["id"]),
            )
            self._log(cur, user["id"], "cliente", "Actualizacion de perfil", "Datos personales actualizados")

    def list_cards(self, user: dict) -> list[dict]:
        require_permission(user, "client_orders")
        self.ensure_schema()
        return self.db.fetch_all(
            """
            SELECT id, alias, titular, marca, ultimos4, vencimiento, favorita
            FROM tarjetas_cliente
            WHERE cliente_id = %s
            ORDER BY favorita DESC, id DESC
            """,
            (user["id"],),
        )

    def save_card(
        self,
        user: dict,
        numero: str,
        titular: str,
        vencimiento: str,
        alias: str | None = None,
        favorita: bool = False,
        card_id: int | None = None,
    ) -> int:
        require_permission(user, "client_orders")
        self.ensure_schema()
        clean_number = "".join(ch for ch in numero if ch.isdigit())
        if not titular.strip():
            raise ValueError("Ingresa el nombre del titular.")
        if not vencimiento.strip():
            raise ValueError("Ingresa la fecha de vencimiento.")

        with self.db.cursor(commit=True) as cur:
            if favorita:
                cur.execute("UPDATE tarjetas_cliente SET favorita = 0 WHERE cliente_id = %s", (user["id"],))
            if card_id:
                cur.execute(
                    "SELECT marca, ultimos4 FROM tarjetas_cliente WHERE id=%s AND cliente_id=%s",
                    (card_id, user["id"]),
                )
                existing = cur.fetchone()
                if not existing:
                    raise ValueError("Tarjeta no encontrada.")
                if clean_number:
                    if len(clean_number) < 12:
                        raise ValueError("Ingresa un numero de tarjeta valido.")
                    marca = self._card_brand(clean_number)
                    ultimos4 = clean_number[-4:]
                else:
                    marca = existing["marca"]
                    ultimos4 = existing["ultimos4"]
                alias = alias or f"{marca} terminacion {ultimos4}"
                cur.execute(
                    """
                    UPDATE tarjetas_cliente
                    SET alias=%s, titular=%s, marca=%s, ultimos4=%s,
                        vencimiento=%s, favorita=%s
                    WHERE id=%s AND cliente_id=%s
                    """,
                    (alias, titular, marca, ultimos4, vencimiento, int(favorita), card_id, user["id"]),
                )
                result_id = card_id
                operation = "Tarjeta actualizada"
            else:
                if len(clean_number) < 12:
                    raise ValueError("Ingresa un numero de tarjeta valido.")
                marca = self._card_brand(clean_number)
                ultimos4 = clean_number[-4:]
                alias = alias or f"{marca} terminacion {ultimos4}"
                cur.execute(
                    """
                    INSERT INTO tarjetas_cliente
                        (cliente_id, alias, titular, marca, ultimos4, vencimiento, favorita)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (user["id"], alias, titular, marca, ultimos4, vencimiento, int(favorita)),
                )
                result_id = cur.lastrowid
                operation = "Tarjeta agregada"
            self._log(cur, user["id"], "cliente", operation, alias)
            return result_id

    def delete_card(self, user: dict, card_id: int):
        require_permission(user, "client_orders")
        self.ensure_schema()
        with self.db.cursor(commit=True) as cur:
            cur.execute(
                "DELETE FROM tarjetas_cliente WHERE id = %s AND cliente_id = %s",
                (card_id, user["id"]),
            )
            self._log(cur, user["id"], "cliente", "Tarjeta eliminada", f"Tarjeta {card_id}")

    def ensure_schema(self):
        with self.db.cursor(commit=True) as cur:
            cur.execute(
                """
                SELECT COUNT(*) AS total
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'usuarios'
                  AND COLUMN_NAME = 'direccion'
                """
            )
            if int(cur.fetchone()["total"]) == 0:
                cur.execute("ALTER TABLE usuarios ADD COLUMN direccion VARCHAR(255) NULL AFTER telefono")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS tarjetas_cliente (
                  id INT AUTO_INCREMENT PRIMARY KEY,
                  cliente_id INT NOT NULL,
                  alias VARCHAR(80) NOT NULL,
                  titular VARCHAR(120) NOT NULL,
                  marca VARCHAR(40) NOT NULL,
                  ultimos4 CHAR(4) NOT NULL,
                  vencimiento VARCHAR(7) NOT NULL,
                  favorita TINYINT(1) NOT NULL DEFAULT 0,
                  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  CONSTRAINT fk_tarjetas_cliente_usuario
                    FOREIGN KEY (cliente_id) REFERENCES usuarios(id)
                ) ENGINE=InnoDB
                """
            )

    @staticmethod
    def _card_brand(number: str) -> str:
        if number.startswith("4"):
            return "Visa"
        if number[:2] in {"51", "52", "53", "54", "55"}:
            return "Mastercard"
        if number.startswith(("34", "37")):
            return "Amex"
        return "Tarjeta"

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
