from decimal import Decimal, InvalidOperation


def required(value: str, field_name: str) -> str:
    clean = (value or "").strip()
    if not clean:
        raise ValueError(f"El campo {field_name} es obligatorio.")
    return clean


def as_decimal(value: str, field_name: str) -> Decimal:
    try:
        amount = Decimal(str(value).strip())
    except (InvalidOperation, AttributeError):
        raise ValueError(f"El campo {field_name} debe ser numerico.")
    if amount < 0:
        raise ValueError(f"El campo {field_name} no puede ser negativo.")
    return amount


def as_int(value: str, field_name: str) -> int:
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        raise ValueError(f"El campo {field_name} debe ser entero.")
    if number < 0:
        raise ValueError(f"El campo {field_name} no puede ser negativo.")
    return number

