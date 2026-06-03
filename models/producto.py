from dataclasses import dataclass


@dataclass
class Producto:
    id: int
    codigo: str
    nombre: str
    marca: str
    categoria: str
    subcategoria: str
    presentacion: str
    precio_venta: float
    stock_actual: int = 0
    stock_minimo: int = 5

