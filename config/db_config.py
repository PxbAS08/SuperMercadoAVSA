import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DbConfig:
    host: str = "127.0.0.1"
    user: str = "root"
    password: str = "PablisQL08$"
    database: str = "avsaware_supermercado"
    port: int = 3306


def get_db_config() -> dict:
    return {
        "host": os.getenv("AVSAWARE_DB_HOST", DbConfig.host),
        "user": os.getenv("AVSAWARE_DB_USER", DbConfig.user),
        "password": os.getenv("AVSAWARE_DB_PASSWORD", DbConfig.password),
        "database": os.getenv("AVSAWARE_DB_NAME", DbConfig.database),
        "port": int(os.getenv("AVSAWARE_DB_PORT", DbConfig.port)),
        "autocommit": False,
    }


def describe_config() -> str:
    cfg = get_db_config()
    return f"{cfg['user']}@{cfg['host']}:{cfg['port']}/{cfg['database']}"

