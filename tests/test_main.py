import sys
from pathlib import Path
from datetime import date

import pytest

# Asegura que src/ esté en el path (por si acaso)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from main import parse_fecha  # noqa: E402


def test_parse_fecha_valida():
    assert parse_fecha("15/10/2026") == date(2026, 10, 15)
    assert parse_fecha("01/01/25") == date(2025, 1, 1)
    assert parse_fecha("2026-12-31") == date(2026, 12, 31)


def test_parse_fecha_invalida():
    with pytest.raises(ValueError):
        parse_fecha("fecha-invalida")