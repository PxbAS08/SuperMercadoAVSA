import sys
from pathlib import Path


BUNDLE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
BASE_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent
ASSETS_DIR = BUNDLE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
COMPROBANTES_DIR = DATA_DIR / "comprobantes"


def ensure_runtime_dirs():
    COMPROBANTES_DIR.mkdir(parents=True, exist_ok=True)


def money(value) -> str:
    return f"${float(value):,.2f}"
