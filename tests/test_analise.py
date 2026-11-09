"""Testes unitários do hiato bruto, geral e por cargo."""

import math

import pytest

from equidade.analise import (
    STATUS_ALERTA,
    STATUS_ATENCAO,
    STATUS_OK,
    STATUS_SEM_COMPARACAO,
    analise_por_cargo,
    hiato_percentual,
    resumo_geral,
)

from .conftest import monta_base


def test_hiato_formula():
    assert hiato_percentual(6000, 5000) == pytest.approx(16.6667, abs=1e-3)
    assert hiato_percentual(5000, 5000) == 0
    assert hiato_percentual(4000, 5000) == pytest.approx(-25.0)  # mulheres ganham mais


@pytest.mark.parametrize("h, m", [(None, 5000), (5000, None), (0, 5000), (5000, -1), (float("nan"), 5000)])
def test_hiato_sem_dado_valido_devolve_none(h, m):
    assert hiato_percentual(h, m) is None


def test_resumo_geral():
    df = monta_base([("M", "Gerente", 6000), ("M", "Gerente", 8000), ("F", "Gerente", 5000), ("F", "Gerente", 7000)])
    r = resumo_geral(df, limite=5.0)
    assert (r["total"], r["homens"], r["mulheres"]) == (4, 2, 2)
    assert r["pct_mulheres"] == 50
    assert r["media_homens"] == 7000 and r["media_mulheres"] == 6000
    assert r["hiato_medias"] == pytest.approx((1 - 6000 / 7000) * 100)
    assert r["alerta"] is True


def test_alerta_so_acima_do_limite():
    df = monta_base([("M", "Gerente", 1000), ("F", "Gerente", 950)])  # hiato exatamente 5%
    assert resumo_geral(df, limite=5.0)["alerta"] is False
    assert resumo_geral(df, limite=4.9)["alerta"] is True


def test_resumo_sem_mulheres_nao_quebra():
    df = monta_base([("M", "Gerente", 6000), ("M", "Gerente", 7000)])
    r = resumo_geral(df)
    assert r["mulheres"] == 0
    assert r["hiato_medias"] is None and r["alerta"] is False
    assert r["media_mulheres"] is None


def _grupo(cargo, n_h, n_m, sal_h, sal_m):
    return [("M", cargo, sal_h)] * n_h + [("F", cargo, sal_m)] * n_m


def test_status_por_cargo_cobre_os_quatro_casos():
    linhas = (
        _grupo("Gerente", 6, 6, 10000, 8000)  # 20% e amostra grande -> alerta
        + _grupo("Coordenador", 2, 2, 10000, 8000)  # 20% mas só 2 por grupo -> atenção
        + [("M", "Diretor", 20000)] * 6  # só homens -> sem comparação
        + _grupo("Supervisor", 6, 6, 10000, 9800)  # 2% -> OK
    )
    tabela = analise_por_cargo(monta_base(linhas), limite=5.0, n_minimo=5)
    assert tabela.loc["Gerente", "status"] == STATUS_ALERTA
    assert tabela.loc["Coordenador", "status"] == STATUS_ATENCAO
    assert tabela.loc["Diretor", "status"] == STATUS_SEM_COMPARACAO
    assert tabela.loc["Supervisor", "status"] == STATUS_OK
    assert tabela.loc["Gerente", "hiato"] == pytest.approx(20.0)
    assert math.isnan(tabela.loc["Diretor", "hiato"])


def test_cargos_vem_na_ordem_hierarquica():
    linhas = _grupo("Diretor", 1, 1, 9, 9) + _grupo("Analista Júnior", 1, 1, 9, 9) + _grupo("Gerente", 1, 1, 9, 9)
    assert list(analise_por_cargo(monta_base(linhas)).index) == ["Analista Júnior", "Gerente", "Diretor"]


def test_mulheres_ganhando_mais_nao_gera_alerta():
    tabela = analise_por_cargo(monta_base(_grupo("Gerente", 6, 6, 8000, 10000)))
    assert tabela.loc["Gerente", "hiato"] == pytest.approx(-25.0)
    assert tabela.loc["Gerente", "status"] == STATUS_OK


def test_p_valor_so_existe_com_pelo_menos_dois_em_cada_grupo():
    linhas = _grupo("Gerente", 1, 4, 10000, 8000)  # só um homem: não há como testar
    tabela = analise_por_cargo(monta_base(linhas))
    assert math.isnan(tabela.loc["Gerente", "p_valor"])


def test_p_valor_baixo_para_diferenca_clara():
    linhas = [("M", "Gerente", s) for s in (10000, 10100, 9900, 10050, 9950)] + [
        ("F", "Gerente", s) for s in (8000, 8100, 7900, 8050, 7950)
    ]
    assert analise_por_cargo(monta_base(linhas)).loc["Gerente", "p_valor"] < 0.001


def test_pct_mulheres_por_cargo():
    tabela = analise_por_cargo(monta_base(_grupo("Gerente", 3, 1, 10, 10)))
    assert tabela.loc["Gerente", "pct_mulheres"] == 25


def test_status_no_limite_exato_nao_e_alerta():
    tabela = analise_por_cargo(monta_base(_grupo("Gerente", 6, 6, 1000, 950)), limite=5.0)
    assert tabela.loc["Gerente", "status"] == STATUS_OK
