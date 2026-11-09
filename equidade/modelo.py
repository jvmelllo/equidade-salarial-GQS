"""Hiato salarial ajustado: regressão do log do salário (mínimos quadrados).

    log(salário) = a + b * mulher + controles + erro

O coeficiente b é a diferença de log-salário entre mulheres e homens com o mesmo
cargo, tempo de empresa e escolaridade (os controles escolhidos). Convertido em
porcentagem, o hiato ajustado é (1 - exp(b)) * 100.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from .dados import ErroDeDados, ordenar_cargos, ordenar_escolaridades

CONTROLES_DISPONIVEIS = ("cargo", "tempo_empresa", "escolaridade")

ROTULOS_CONTROLES = {
    "cargo": "cargo",
    "tempo_empresa": "tempo de empresa",
    "escolaridade": "escolaridade",
}


@dataclass(frozen=True)
class ResultadoModelo:
    controles: tuple[str, ...]
    hiato: float  # em %
    ic_inferior: float  # em %
    ic_superior: float  # em %
    p_valor: float
    n: int
    r2: float
    coeficientes: pd.DataFrame  # termo, coeficiente, erro_padrao, efeito_pct, p_valor


def _colunas_do_controle(df: pd.DataFrame, controle: str) -> tuple[list[str], list[np.ndarray]]:
    """Colunas da matriz X para um controle. Categorias usam a primeira da hierarquia como referência."""
    if controle == "tempo_empresa":
        return ["tempo de empresa (por ano)"], [df["tempo_empresa"].to_numpy(float)]
    if controle == "cargo":
        categorias = ordenar_cargos(df["cargo"].unique())
    else:
        categorias = ordenar_escolaridades(df["escolaridade"].unique())
    nomes = [f"{ROTULOS_CONTROLES[controle]}: {c}" for c in categorias[1:]]
    colunas = [(df[controle] == c).to_numpy(float) for c in categorias[1:]]
    return nomes, colunas


def estimar_hiato(
    df: pd.DataFrame,
    controles=CONTROLES_DISPONIVEIS,
    nivel_confianca: float = 0.95,
) -> ResultadoModelo:
    """Estima o hiato salarial controlando por `controles`.

    Controles cuja coluna não existe na base são ignorados. Nomes fora de
    CONTROLES_DISPONIVEIS levantam ValueError.
    """
    desconhecidos = [c for c in controles if c not in CONTROLES_DISPONIVEIS]
    if desconhecidos:
        raise ValueError(f"Controles desconhecidos: {desconhecidos}")
    controles = tuple(c for c in controles if c in df.columns)

    if set(df["genero"].unique()) != {"M", "F"}:
        raise ErroDeDados("O modelo precisa de homens e mulheres na base.")

    nomes = ["intercepto", "mulher"]
    colunas = [np.ones(len(df)), (df["genero"] == "F").to_numpy(float)]
    for controle in controles:
        novos_nomes, novas_colunas = _colunas_do_controle(df, controle)
        nomes += novos_nomes
        colunas += novas_colunas

    x = np.column_stack(colunas)
    y = np.log(df["salario"].to_numpy(float))
    n, k = x.shape
    if n <= k:
        raise ErroDeDados(f"Poucas linhas ({n}) para estimar {k} parâmetros. Use menos controles.")
    if np.linalg.matrix_rank(x) < k:
        raise ErroDeDados(
            "Os controles escolhidos são redundantes entre si (por exemplo, uma coluna "
            "constante). Tire algum controle."
        )

    xtx_inv = np.linalg.inv(x.T @ x)
    beta = xtx_inv @ x.T @ y
    residuos = y - x @ beta
    graus = n - k
    sigma2 = float(residuos @ residuos) / graus
    erro_padrao = np.sqrt(np.diag(xtx_inv) * sigma2)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = beta / erro_padrao
    p_valores = 2 * stats.t.sf(np.abs(t), graus)
    t_critico = stats.t.ppf(0.5 + nivel_confianca / 2, graus)

    b, e = beta[1], erro_padrao[1]
    soma_total = float(((y - y.mean()) ** 2).sum())
    efeito_pct = (np.exp(beta) - 1) * 100
    efeito_pct[0] = np.nan  # o intercepto não tem leitura como efeito percentual
    coeficientes = pd.DataFrame(
        {
            "termo": nomes,
            "coeficiente": beta,
            "erro_padrao": erro_padrao,
            "efeito_pct": efeito_pct,
            "p_valor": p_valores,
        }
    )
    return ResultadoModelo(
        controles=controles,
        hiato=float((1 - np.exp(b)) * 100),
        ic_inferior=float((1 - np.exp(b + t_critico * e)) * 100),
        ic_superior=float((1 - np.exp(b - t_critico * e)) * 100),
        p_valor=float(p_valores[1]),
        n=n,
        r2=1 - float(residuos @ residuos) / soma_total if soma_total > 0 else float("nan"),
        coeficientes=coeficientes,
    )


def descrever_controles(controles) -> str:
    if not controles:
        return "Sem controles"
    return "Controla por " + ", ".join(ROTULOS_CONTROLES[c] for c in controles)


def comparar_especificacoes(df: pd.DataFrame, nivel_confianca: float = 0.95) -> pd.DataFrame:
    """Hiato estimado com controles cada vez mais completos.

    Mostra quanto do hiato bruto some quando se compara pessoas parecidas e
    quanto sobra. Especificações que não podem ser estimadas ficam de fora.
    """
    disponiveis = [c for c in CONTROLES_DISPONIVEIS if c in df.columns]
    sem_cargo = tuple(c for c in disponiveis if c != "cargo")
    candidatas = [(), sem_cargo, tuple(disponiveis)]
    vistas, linhas = set(), []
    for controles in candidatas:
        if controles in vistas:
            continue
        vistas.add(controles)
        try:
            r = estimar_hiato(df, controles, nivel_confianca)
        except ErroDeDados:
            continue
        linhas.append(
            {
                "especificacao": descrever_controles(controles),
                "controles": ", ".join(controles),
                "hiato": r.hiato,
                "ic_inferior": r.ic_inferior,
                "ic_superior": r.ic_superior,
                "p_valor": r.p_valor,
                "n": r.n,
            }
        )
    return pd.DataFrame(
        linhas,
        columns=["especificacao", "controles", "hiato", "ic_inferior", "ic_superior", "p_valor", "n"],
    )
