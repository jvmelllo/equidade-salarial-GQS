"""Formatação de números no padrão brasileiro (vírgula decimal, ponto de milhar)."""

from __future__ import annotations

import math


def _valido(valor) -> bool:
    return valor is not None and not (isinstance(valor, float) and math.isnan(valor))


def pct(valor, casas: int = 1) -> str:
    """13.94 -> '13,9%'. Valores ausentes viram '—'."""
    if not _valido(valor):
        return "—"
    return f"{valor:.{casas}f}".replace(".", ",") + "%"


def numero(valor, casas: int = 0) -> str:
    """10731.8 -> '10.732'."""
    if not _valido(valor):
        return "—"
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def brl(valor, casas: int = 0) -> str:
    """10731.8 -> 'R$ 10.732'."""
    if not _valido(valor):
        return "—"
    return "R$ " + numero(valor, casas)
