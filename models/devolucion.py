from dataclasses import dataclass
from datetime import datetime


@dataclass
class Devolucion:
    id: int
    venta_id: int
    motivo: str
    monto: float
    tipo_reembolso: str
    estado: str
    created_at: datetime

