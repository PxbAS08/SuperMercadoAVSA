from dataclasses import dataclass
from datetime import datetime


@dataclass
class Pedido:
    id: int
    cliente_id: int
    modalidad_entrega: str
    forma_pago: str
    estado: str
    total: float
    created_at: datetime

