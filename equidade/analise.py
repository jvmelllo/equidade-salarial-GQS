"""Hiato salarial bruto: geral e por cargo."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy import stats

from .dados import ordenar_cargos

LIMITE_ALERTA_PADRAO = 5.0  # em pontos percentuais
N_MINIMO_PADRAO = 5  # pessoas por grupo (homens e mulheres) para confiar na comparação

STATUS_ALERTA = "Alerta"
STATUS_ATENCAO = "Atenção (amostra pequena)"
STATUS_OK = "OK"
STATUS_SEM_COMPARACAO = "Sem comparação"

COLUNAS_POR_CARGO = [
    "n_homens",
    "n_mulheres",
    "pct_mulheres",
    "media_homens",
    "media_mulheres",
    "hiato",
    "p_valor",
    "status",
]


def _valido(valor) -> bool:
    return valor is not None and not math.isnan(valor) and valor > 0


def hiato_percentual(media_homens, media_mulheres) -> float | None:
    """Quanto a menos as mulheres ganham em relação aos homens, em %.

    hiato = (1 - média das mulheres / média dos homens) * 100.
    Valor negativo significa que as mulheres ganham mais. Sem dado, devolve None.
    """
    if not _valido(media_homens) or not _valido(media_mulheres):
        return None
    return float((1 - media_mulheres / media_homens) * 100)


def acima_do_limite(hiato: float | None, limite: float) -> bool:
    """True quando o hiato passa do limite. Arredonda antes de comparar, para que
    um hiato de exatamente 5% (5,000000000000004 em ponto flutuante) não dispare alerta."""
    return hiato is not None and round(hiato, 6) > limite


def _media(serie: pd.Series) -> float | None:
    return float(serie.mean()) if len(serie) else None


def _mediana(serie: pd.Series) -> float | None:
    return float(serie.median()) if len(serie) else None


def resumo_geral(df: pd.DataFrame, limite: float = LIMITE_ALERTA_PADRAO) -> dict:
    """Indicadores gerais da base e o alerta de hiato acima do limite."""
    homens = df.loc[df["genero"] == "M", "salario"]
    mulheres = df.loc[df["genero"] == "F", "salario"]
    hiato_medias = hiato_percentual(_media(homens), _media(mulheres))
    hiato_medianas = hiato_percentual(_mediana(homens), _mediana(mulheres))
    total = len(df)
    return {
        "total": total,
        "homens": len(homens),
        "mulheres": len(mulheres),
        "pct_mulheres": len(mulheres) / total * 100 if total else None,
        "media_homens": _media(homens),
        "media_mulheres": _media(mulheres),
        "mediana_homens": _mediana(homens),
        "mediana_mulheres": _mediana(mulheres),
        "hiato_medias": hiato_medias,
        "hiato_medianas": hiato_medianas,
        "limite": limite,
        "alerta": acima_do_limite(hiato_medias, limite),
    }


def _p_valor(homens: pd.Series, mulheres: pd.Series) -> float:
    """Teste t de Welch entre os dois grupos. NaN quando não há como testar."""
    if len(homens) < 2 or len(mulheres) < 2:
        return float("nan")
    if homens.std() == 0 and mulheres.std() == 0:
        return float("nan")
    return float(stats.ttest_ind(homens, mulheres, equal_var=False).pvalue)


def _status(hiato, n_homens: int, n_mulheres: int, limite: float, n_minimo: int) -> str:
    if hiato is None:
        return STATUS_SEM_COMPARACAO
    if acima_do_limite(hiato, limite):
        return STATUS_ATENCAO if min(n_homens, n_mulheres) < n_minimo else STATUS_ALERTA
    return STATUS_OK


def analise_por_cargo(
    df: pd.DataFrame,
    limite: float = LIMITE_ALERTA_PADRAO,
    n_minimo: int = N_MINIMO_PADRAO,
) -> pd.DataFrame:
    """Uma linha por cargo, na ordem hierárquica.

    O p-valor é informativo: com vários cargos testados, alguns "significativos"
    aparecem por acaso. Por isso o alerta usa o limite e o tamanho da amostra.
    """
    linhas = []
    for cargo in ordenar_cargos(df["cargo"].unique()):
        grupo = df[df["cargo"] == cargo]
        homens = grupo.loc[grupo["genero"] == "M", "salario"]
        mulheres = grupo.loc[grupo["genero"] == "F", "salario"]
        media_h, media_m = _media(homens), _media(mulheres)
        hiato = hiato_percentual(media_h, media_m)
        linhas.append(
            {
                "cargo": cargo,
                "n_homens": len(homens),
                "n_mulheres": len(mulheres),
                "pct_mulheres": len(mulheres) / len(grupo) * 100,
                "media_homens": media_h if media_h is not None else np.nan,
                "media_mulheres": media_m if media_m is not None else np.nan,
                "hiato": hiato if hiato is not None else np.nan,
                "p_valor": _p_valor(homens, mulheres),
                "status": _status(hiato, len(homens), len(mulheres), limite, n_minimo),
            }
        )
    tabela = pd.DataFrame(linhas, columns=["cargo", *COLUNAS_POR_CARGO])
    return tabela.set_index("cargo")
