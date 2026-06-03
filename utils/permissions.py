ADMIN = "ADMIN"
CLIENTE = "CLIENTE"

PERMISSIONS = {
    ADMIN: {
        "dashboard_admin",
        "users_manage",
        "roles_manage",
        "products_read",
        "products_write",
        "categories_manage",
        "inventory_read",
        "inventory_write",
        "sales_write",
        "sales_read_all",
        "returns_write",
        "orders_manage",
        "reports_admin",
    },
    CLIENTE: {
        "client_shop",
        "client_orders",
        "client_history",
        "client_wallet",
    },
}


def role_of(user: dict | None) -> str:
    return (user or {}).get("rol", "")


def can(user: dict | None, permission: str) -> bool:
    return permission in PERMISSIONS.get(role_of(user), set())


def require_permission(user: dict | None, permission: str):
    if not can(user, permission):
        raise PermissionError("No tienes permisos para acceder a esta seccion.")
