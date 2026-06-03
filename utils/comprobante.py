from datetime import datetime
from pathlib import Path

from utils.helpers import COMPROBANTES_DIR, ensure_runtime_dirs, money


def build_receipt(
    folio: str,
    user_name: str,
    items: list[dict],
    subtotal: float,
    descuento: float,
    total: float,
    forma_pago: str,
    modalidad_entrega: str,
    cliente: str | None = None,
    direccion: str | None = None,
    pago_recibido: float | None = None,
    cambio: float | None = None,
) -> str:
    lines = [
        "AVSAware - Sistema de Gestion para Supermercado",
        "Comprobante interno de venta",
        f"Folio: {folio}",
        f"Fecha: {datetime.now():%Y-%m-%d %H:%M:%S}",
        f"Usuario: {user_name}",
    ]
    if cliente:
        lines.append(f"Cliente: {cliente}")
    lines.extend(
        [
            f"Forma de pago: {forma_pago}",
            f"Modalidad: {modalidad_entrega}",
        ]
    )
    if direccion:
        lines.append(f"Direccion: {direccion}")
    lines.extend(["", "Productos:", "-" * 58])

    for item in items:
        name = item["nombre"]
        qty = int(item["cantidad"])
        price = float(item["precio_unitario"])
        lines.append(f"{qty:>3} x {name[:34]:34} {money(qty * price):>12}")

    lines.extend(
        [
            "-" * 58,
            f"Subtotal:  {money(subtotal)}",
            f"Descuento: {money(descuento)}",
            f"Total:     {money(total)}",
        ]
    )
    if pago_recibido is not None:
        lines.append(f"Pago recibido: {money(pago_recibido)}")
    if cambio is not None:
        lines.append(f"Cambio:        {money(cambio)}")
    lines.extend(["", "Gracias por utilizar AVSAware."])
    return "\n".join(lines)


def save_receipt(folio: str, content: str) -> Path:
    ensure_runtime_dirs()
    safe_folio = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in folio)
    path = COMPROBANTES_DIR / f"{safe_folio}.txt"
    path.write_text(content, encoding="utf-8")
    return path
