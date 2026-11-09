"""Gráficos (matplotlib) usados no painel e no README.

Cores fixas por entidade em todos os gráficos: azul = homens, laranja = mulheres.
Alerta usa vermelho de status, atenção usa amarelo de status e "dentro do limite"
fica em cinza, para o olhar ir primeiro aos cargos com problema.
Todas as funções devolvem uma `matplotlib.figure.Figure` (sem estado global).
"""

from __future__ import annotations

import textwrap

import matplotlib
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MaxNLocator

from .analise import STATUS_ALERTA, STATUS_ATENCAO, STATUS_OK
from .formatacao import numero, pct

SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
MUDO = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"

COR_HOMENS = "#2a78d6"
COR_MULHERES = "#eb6834"
COR_ALERTA = "#d03b3b"
COR_ATENCAO = "#fab219"
COR_NEUTRA = MUDO

_COR_STATUS = {STATUS_ALERTA: COR_ALERTA, STATUS_ATENCAO: COR_ATENCAO, STATUS_OK: COR_NEUTRA}

_RC = {
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.edgecolor": EIXO,
    "axes.labelcolor": TINTA_SECUNDARIA,
    "xtick.color": MUDO,
    "ytick.color": TINTA_SECUNDARIA,
    "text.color": TINTA,
    "figure.facecolor": SUPERFICIE,
    "axes.facecolor": SUPERFICIE,
    "savefig.facecolor": SUPERFICIE,
}


def salvar(fig: Figure, caminho, dpi: int = 160) -> None:
    fig.savefig(caminho, dpi=dpi, bbox_inches="tight")


def _novo(largura: float, altura: float, titulo: str | None, subtitulo: str | None):
    """Cria figura e eixo com a aparência comum: grade horizontal discreta, sem molduras."""
    with matplotlib.rc_context(_RC):
        fig = Figure(figsize=(largura, altura), layout="constrained")
        ax = fig.subplots()
    ax.grid(axis="x", color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", length=0)
    if titulo:
        ax.set_title(titulo, loc="left", fontsize=13, fontweight="bold", color=TINTA, pad=26 if subtitulo else 10)
    if subtitulo:
        ax.annotate(subtitulo, (0, 1), xycoords="axes fraction", xytext=(0, 5), textcoords="offset points",
                    fontsize=9.5, color=TINTA_SECUNDARIA, va="bottom")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=7, steps=[1, 2, 5, 10]))
    return fig, ax


def _eixo_pct(valor, _posicao) -> str:
    return f"{valor:.0f}%".replace("-", "−")


def _figura_vazia(mensagem: str, titulo: str | None) -> Figure:
    """Figura com um aviso, para quando não há o que comparar."""
    fig, ax = _novo(8.2, 2.2, titulo, None)
    ax.set_axis_off()
    ax.text(0.5, 0.5, mensagem, ha="center", va="center", transform=ax.transAxes,
            color=TINTA_SECUNDARIA, fontsize=11)
    return fig


def grafico_hiato_por_cargo(
    por_cargo: pd.DataFrame,
    limite: float,
    n_minimo: int,
    titulo: str | None = "Hiato salarial por cargo",
) -> Figure:
    """Barras horizontais com o hiato de cada cargo; só os que passam do limite recebem rótulo."""
    dados = por_cargo.dropna(subset=["hiato"])
    if dados.empty:
        return _figura_vazia("Nenhum cargo tem homens e mulheres ao mesmo tempo para comparar.", titulo)
    n = len(dados)
    subtitulo = "Quanto a menos as mulheres ganham que os homens, em média, no mesmo cargo" if titulo else None
    fig, ax = _novo(8.2, 0.55 * n + 2.2, titulo, subtitulo)

    posicoes = np.arange(len(dados))
    cores = [_COR_STATUS.get(s, COR_NEUTRA) for s in dados["status"]]
    ax.barh(posicoes, dados["hiato"], height=0.42, color=cores, edgecolor=SUPERFICIE, linewidth=2, zorder=3)
    ax.set_yticks(posicoes, labels=list(dados.index))
    ax.axvline(0, color=EIXO, linewidth=1.2, zorder=4)
    ax.axvline(limite, color=TINTA_SECUNDARIA, linewidth=1, zorder=4)
    ax.text(limite, len(dados) - 0.35, f" limite de {pct(limite, 0)}", color=TINTA_SECUNDARIA, fontsize=8.5, va="bottom")

    for pos, (_, linha) in zip(posicoes, dados.iterrows()):
        if linha["status"] in (STATUS_ALERTA, STATUS_ATENCAO):
            texto = pct(linha["hiato"])
            if linha["status"] == STATUS_ATENCAO:
                texto += "  amostra pequena"
            ax.annotate(texto, (linha["hiato"], pos), xytext=(6, 0), textcoords="offset points",
                        va="center", fontsize=9, color=TINTA)

    ax.xaxis.set_major_formatter(FuncFormatter(_eixo_pct))
    ax.set_xlim(min(dados["hiato"].min() - 2, -2), max(dados["hiato"].max() * 1.3, limite + 4))
    ax.set_xlabel("Hiato salarial (valores negativos: mulheres ganham mais)")
    ax.set_ylim(-0.6, len(dados) + 0.1)
    legendas = {
        STATUS_ALERTA: Patch(color=COR_ALERTA, label="Acima do limite"),
        STATUS_ATENCAO: Patch(color=COR_ATENCAO, label=f"Acima do limite, menos de {n_minimo} pessoas em um grupo"),
        STATUS_OK: Patch(color=COR_NEUTRA, label="Dentro do limite"),
    }
    presentes = [legendas[s] for s in legendas if s in set(dados["status"])]
    if presentes:
        fig.legend(handles=presentes, loc="outside lower center", ncol=len(presentes), frameon=False,
                   fontsize=8.5, labelcolor=TINTA_SECUNDARIA)
    return fig


def grafico_medias_por_cargo(
    por_cargo: pd.DataFrame, titulo: str | None = "Salário médio por cargo e gênero"
) -> Figure:
    """Barras agrupadas (homens e mulheres) por cargo; o valor fica no eixo e na tabela."""
    dados = por_cargo
    n = max(len(dados), 1)
    fig, ax = _novo(8.2, 0.7 * n + 2.0, titulo, "Média salarial mensal, em R$ mil" if titulo else None)
    posicoes = np.arange(len(dados))
    altura = 0.30
    ax.barh(posicoes + altura / 2, dados["media_homens"].fillna(0) / 1000, height=altura,
            color=COR_HOMENS, edgecolor=SUPERFICIE, linewidth=2, zorder=3)
    ax.barh(posicoes - altura / 2, dados["media_mulheres"].fillna(0) / 1000, height=altura,
            color=COR_MULHERES, edgecolor=SUPERFICIE, linewidth=2, zorder=3)
    ax.set_yticks(posicoes, labels=list(dados.index))
    ax.axvline(0, color=EIXO, linewidth=1.2, zorder=4)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _p: numero(v)))
    ax.set_xlabel("R$ mil")
    ax.set_ylim(-0.6, len(dados) - 0.4)
    ax.legend(
        handles=[Patch(color=COR_HOMENS, label="Homens"), Patch(color=COR_MULHERES, label="Mulheres")],
        loc="lower right", frameon=False, fontsize=9, labelcolor=TINTA_SECUNDARIA,
    )
    return fig


def grafico_representacao(
    por_cargo: pd.DataFrame, titulo: str | None = "Participação feminina por cargo"
) -> Figure:
    """Percentual de mulheres em cada cargo; só o primeiro e o último nível recebem rótulo."""
    dados = por_cargo
    n = max(len(dados), 1)
    fig, ax = _novo(8.2, 0.5 * n + 1.9, titulo, "Mulheres como % das pessoas do cargo" if titulo else None)
    posicoes = np.arange(len(dados))
    ax.barh(posicoes, dados["pct_mulheres"], height=0.42, color=COR_MULHERES,
            edgecolor=SUPERFICIE, linewidth=2, zorder=3)
    ax.set_yticks(posicoes, labels=list(dados.index))
    ax.axvline(0, color=EIXO, linewidth=1.2, zorder=4)
    ax.axvline(50, color=TINTA_SECUNDARIA, linewidth=1, zorder=4)
    ax.text(50, len(dados) - 0.35, " paridade (50%)", color=TINTA_SECUNDARIA, fontsize=8.5, va="bottom")
    for pos in (0, len(dados) - 1):
        valor = dados["pct_mulheres"].iloc[pos]
        ax.annotate(pct(valor, 0), (valor, pos), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=9, color=TINTA)
    ax.set_xlim(0, max(65, float(dados["pct_mulheres"].max()) + 10))
    ax.xaxis.set_major_formatter(FuncFormatter(_eixo_pct))
    ax.set_ylim(-0.6, len(dados) + 0.1)
    ax.set_xlabel("% de mulheres")
    return fig


def grafico_especificacoes(
    especificacoes: pd.DataFrame, titulo: str | None = "Hiato salarial com controles cada vez mais completos"
) -> Figure:
    """Ponto e intervalo de confiança do hiato em cada especificação do modelo."""
    dados = especificacoes.reset_index(drop=True)
    if dados.empty:
        return _figura_vazia("Não foi possível estimar o modelo com esta base.", titulo)
    n = len(dados)
    subtitulo = "Estimativa do modelo (log do salário) e intervalo de confiança de 95%" if titulo else None
    fig, ax = _novo(8.2, 0.85 * n + 1.9, titulo, subtitulo)
    posicoes = np.arange(len(dados))[::-1]  # primeira especificação no topo
    ax.hlines(posicoes, dados["ic_inferior"], dados["ic_superior"], color=COR_MULHERES, linewidth=2, zorder=3)
    ax.plot(dados["hiato"], posicoes, "o", color=COR_MULHERES, markersize=9,
            markeredgecolor=SUPERFICIE, markeredgewidth=2, zorder=5)
    ax.set_yticks(posicoes, labels=[textwrap.fill(r, 26) for r in dados["especificacao"]])
    ax.axvline(0, color=EIXO, linewidth=1.2, zorder=4)
    for pos, (_, linha) in zip(posicoes, dados.iterrows()):
        ax.annotate(pct(linha["hiato"]), (linha["hiato"], pos), xytext=(0, 11), textcoords="offset points",
                    ha="center", fontsize=9, color=TINTA)
    limite_dir = max(dados["ic_superior"].max(), 1) * 1.15
    ax.set_xlim(min(dados["ic_inferior"].min() - 1, -1), limite_dir)
    ax.set_ylim(-0.6, len(dados) - 0.4)
    ax.xaxis.set_major_formatter(FuncFormatter(_eixo_pct))
    ax.set_xlabel("Hiato salarial (quanto a menos as mulheres ganham)")
    return fig
