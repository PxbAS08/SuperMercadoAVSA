from dataclasses import dataclass
from datetime import datetime


@dataclass
class Venta:
    id: int
    folio: str
    usuario_id: int
    subtotal: float
    descuento: float
    total: float
    estado: str
    created_at: datetime

