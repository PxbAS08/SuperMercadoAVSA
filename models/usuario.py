from dataclasses import dataclass


@dataclass
class Usuario:
    id: int
    username: str
    nombre: str
    rol: str
    saldo_electronico: float = 0.0
    activo: bool = True

