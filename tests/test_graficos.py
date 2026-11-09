"""Os gráficos devem ser gerados sem erro, inclusive com dados incompletos."""

import io

import numpy as np
import pytest
from matplotlib.figure import Figure

from equidade import analise, graficos, modelo

from .conftest import monta_base


def _png(fig) -> bytes:
    buffer = io.BytesIO()
    graficos.salvar(fig, buffer, dpi=60)
    return buffer.getvalue()


@pytest.fixture
def tabelas(exemplo):
    return analise.analise_por_cargo(exemplo), modelo.comparar_especificacoes(exemplo)


def test_todos_os_graficos_viram_png(tabelas):
    por_cargo, especificacoes = tabelas
    figuras = [
        graficos.grafico_hiato_por_cargo(por_cargo, 5.0, 5),
        graficos.grafico_medias_por_cargo(por_cargo),
        graficos.grafico_representacao(por_cargo),
        graficos.grafico_especificacoes(especificacoes),
    ]
    for fig in figuras:
        assert isinstance(fig, Figure)
        assert _png(fig).startswith(b"\x89PNG")


def test_graficos_aceitam_titulo_nulo_para_uso_no_painel(tabelas):
    por_cargo, especificacoes = tabelas
    assert _png(graficos.grafico_hiato_por_cargo(por_cargo, 5.0, 5, titulo=None))
    assert _png(graficos.grafico_especificacoes(especificacoes, titulo=None))


def test_cargo_so_com_homens_nao_quebra_os_graficos():
    base = monta_base(
        [("M", "Gerente", 10)] * 6 + [("F", "Gerente", 8)] * 6 + [("M", "Diretor", 20)] * 6
    )
    por_cargo = analise.analise_por_cargo(base)
    assert np.isnan(por_cargo.loc["Diretor", "hiato"])
    assert _png(graficos.grafico_hiato_por_cargo(por_cargo, 5.0, 5))
    assert _png(graficos.grafico_medias_por_cargo(por_cargo))
    assert _png(graficos.grafico_representacao(por_cargo))


def test_hiato_com_amostra_pequena_aparece_na_legenda():
    base = monta_base([("M", "Gerente", 10)] * 2 + [("F", "Gerente", 8)] * 2)
    fig = graficos.grafico_hiato_por_cargo(analise.analise_por_cargo(base), 5.0, 5)
    textos = [t.get_text() for legenda in fig.legends for t in legenda.get_texts()]
    assert any("menos de 5 pessoas" in t for t in textos)


def test_sem_nenhum_cargo_comparavel_mostra_aviso_em_vez_de_quebrar():
    base = monta_base([("M", "Gerente", 10)] * 6 + [("F", "Diretor", 20)] * 6)
    por_cargo = analise.analise_por_cargo(base)
    assert por_cargo["hiato"].isna().all()
    fig = graficos.grafico_hiato_por_cargo(por_cargo, 5.0, 5)
    assert any("Nenhum cargo" in t.get_text() for t in fig.axes[0].texts)
    assert _png(fig)


def test_especificacoes_vazias_mostram_aviso():
    import pandas as pd

    vazio = pd.DataFrame(columns=["especificacao", "controles", "hiato", "ic_inferior", "ic_superior", "p_valor", "n"])
    assert _png(graficos.grafico_especificacoes(vazio))
