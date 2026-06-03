import hashlib

from database.connection import Database
from utils.permissions import require_permission


class AuthController:
    def __init__(self, db: Database | None = None):
        self.db = db or Database()

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def login(self, username: str, password: str) -> dict | None:
        self.ensure_user_profile_schema()
        query = """
            SELECT u.id, u.username, u.nombre, u.email, u.telefono, u.activo,
                   u.direccion, u.saldo_electronico, r.nombre AS rol
            FROM usuarios u
            JOIN roles r ON r.id = u.rol_id
            WHERE u.username = %s
              AND u.password_hash = %s
              AND u.activo = 1
        """
        user = self.db.fetch_one(query, (username, self.hash_password(password)))
        if user:
            if user["rol"] not in {"ADMIN", "CLIENTE"}:
                raise ValueError("Este rol ya no esta habilitado. Usa una cuenta de administrador o cliente.")
            self.log_operation(user["id"], "auth", "login", "Inicio de sesion")
        return user

    def register_client(self, username: str, password: str, nombre: str | None = None) -> int:
        return self.create_user(username, password, nombre or username, "CLIENTE")

    def create_user(
        self,
        username: str,
        password: str,
        nombre: str,
        rol: str,
        email: str | None = None,
        telefono: str | None = None,
        direccion: str | None = None,
        actor: dict | None = None,
    ) -> int:
        if actor is not None:
            require_permission(actor, "users_manage")
        self.ensure_user_profile_schema()
        with self.db.cursor(commit=True) as cur:
            cur.execute("SELECT id FROM roles WHERE nombre = %s", (rol,))
            role_row = cur.fetchone()
            if not role_row:
                raise ValueError(f"Rol no registrado: {rol}")
            cur.execute(
                """
                INSERT INTO usuarios
                    (username, password_hash, nombre, email, telefono, direccion, rol_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    username,
                    self.hash_password(password),
                    nombre,
                    email,
                    telefono,
                    direccion,
                    role_row["id"],
                ),
            )
            user_id = cur.lastrowid
            if actor is not None:
                cur.execute(
                    """
                    INSERT INTO historial_operaciones
                        (usuario_id, modulo, operacion, descripcion)
                    VALUES (%s, 'usuarios', 'Alta de usuario', %s)
                    """,
                    (actor["id"], f"{username} - {rol}"),
                )
            return user_id

    def list_users(self, actor: dict | None = None) -> list[dict]:
        if actor is not None:
            require_permission(actor, "users_manage")
        self.ensure_user_profile_schema()
        return self.db.fetch_all(
            """
            SELECT u.id, u.username, u.nombre, u.email, u.telefono,
                   u.direccion, r.nombre AS rol, u.activo, u.saldo_electronico
            FROM usuarios u
            JOIN roles r ON r.id = u.rol_id
            WHERE r.nombre IN ('ADMIN', 'CLIENTE')
            ORDER BY u.id
            """
        )

    def list_roles(self, actor: dict | None = None) -> list[str]:
        if actor is not None:
            require_permission(actor, "roles_manage")
        rows = self.db.fetch_all("SELECT nombre FROM roles WHERE nombre IN ('ADMIN', 'CLIENTE') ORDER BY id")
        return [row["nombre"] for row in rows]

    def update_profile(
        self,
        user_id: int,
        nombre: str,
        email: str | None,
        telefono: str | None,
        direccion: str | None,
        actor: dict,
    ):
        self.ensure_user_profile_schema()
        if actor.get("id") != user_id:
            require_permission(actor, "users_manage")
        with self.db.cursor(commit=True) as cur:
            cur.execute(
                """
                UPDATE usuarios
                SET nombre=%s, email=%s, telefono=%s, direccion=%s
                WHERE id=%s
                """,
                (nombre, email, telefono, direccion, user_id),
            )
            cur.execute(
                """
                INSERT INTO historial_operaciones
                    (usuario_id, modulo, operacion, descripcion)
                VALUES (%s, 'usuarios', 'Actualizacion de perfil', %s)
                """,
                (actor["id"], f"Usuario {user_id}"),
            )

    def deactivate_user(self, user_id: int, actor: dict):
        require_permission(actor, "users_manage")
        if int(user_id) == int(actor["id"]):
            raise ValueError("No puedes eliminar tu propio usuario administrador.")
        with self.db.cursor(commit=True) as cur:
            cur.execute(
                """
                SELECT u.id, u.username, r.nombre AS rol, u.activo
                FROM usuarios u
                JOIN roles r ON r.id = u.rol_id
                WHERE u.id = %s
                """,
                (user_id,),
            )
            user = cur.fetchone()
            if not user:
                raise ValueError("Usuario no encontrado.")
            if user["rol"] == "ADMIN":
                cur.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM usuarios u
                    JOIN roles r ON r.id = u.rol_id
                    WHERE r.nombre = 'ADMIN' AND u.activo = 1 AND u.id <> %s
                    """,
                    (user_id,),
                )
                if int(cur.fetchone()["total"]) == 0:
                    raise ValueError("No puedes eliminar el ultimo administrador activo.")
            cur.execute("UPDATE usuarios SET activo = 0 WHERE id = %s", (user_id,))
            cur.execute(
                """
                INSERT INTO historial_operaciones
                    (usuario_id, modulo, operacion, descripcion)
                VALUES (%s, 'usuarios', 'Usuario desactivado', %s)
                """,
                (actor["id"], f"{user['username']} ({user['rol']})"),
            )

    def ensure_user_profile_schema(self):
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

    def log_operation(self, usuario_id: int, modulo: str, operacion: str, descripcion: str):
        self.db.execute(
            """
            INSERT INTO historial_operaciones
                (usuario_id, modulo, operacion, descripcion)
            VALUES (%s, %s, %s, %s)
            """,
            (usuario_id, modulo, operacion, descripcion),
        )
