"""Testes do modelo de hiato ajustado (regressão do log do salário)."""

import numpy as np
import pandas as pd
import pytest

from equidade.dados import ErroDeDados
from equidade.modelo import comparar_especificacoes, estimar_hiato


def simula(n=3000, hiato_verdadeiro=0.10, semente=7, ruido=0.08):
    """Base sintética com hiato conhecido: o modelo deve recuperá-lo."""
    rng = np.random.default_rng(semente)
    cargo = rng.choice(["Analista Júnior", "Analista Pleno", "Gerente"], size=n, p=[0.4, 0.4, 0.2])
    # mulheres concentradas em cargos baixos: o hiato bruto fica maior que o verdadeiro
    prob_mulher = np.where(cargo == "Gerente", 0.2, 0.55)
    genero = np.where(rng.random(n) < prob_mulher, "F", "M")
    tempo = rng.integers(0, 15, size=n).astype(float)
    escolaridade = rng.choice(["Superior", "Mestrado"], size=n)
    base = pd.Series(cargo).map({"Analista Júnior": 4000, "Analista Pleno": 6500, "Gerente": 15000}).to_numpy()
    log_salario = (
        np.log(base)
        + 0.01 * tempo
        + np.where(escolaridade == "Mestrado", 0.10, 0.0)
        + np.where(genero == "F", np.log(1 - hiato_verdadeiro), 0.0)
        + rng.normal(0, ruido, n)
    )
    return pd.DataFrame(
        {"genero": genero, "cargo": cargo, "salario": np.exp(log_salario),
         "tempo_empresa": tempo, "escolaridade": escolaridade}
    )


def test_recupera_o_hiato_verdadeiro_com_controles():
    r = estimar_hiato(simula(hiato_verdadeiro=0.10))
    assert r.hiato == pytest.approx(10.0, abs=1.0)
    assert r.ic_inferior < 10.0 < r.ic_superior
    assert r.p_valor < 0.001
    assert r.n == 3000


def test_sem_diferenca_verdadeira_o_intervalo_inclui_zero():
    r = estimar_hiato(simula(hiato_verdadeiro=0.0))
    assert r.ic_inferior < 0 < r.ic_superior
    assert r.p_valor > 0.05


def test_sem_controles_e_a_diferenca_das_medias_geometricas():
    df = simula()
    esperado = (1 - np.exp(np.log(df.loc[df.genero == "F", "salario"]).mean()
                           - np.log(df.loc[df.genero == "M", "salario"]).mean())) * 100
    assert estimar_hiato(df, controles=()).hiato == pytest.approx(esperado, rel=1e-9)


def test_coeficientes_batem_com_o_minimos_quadrados_do_numpy():
    df = simula(n=500)
    r = estimar_hiato(df, controles=("tempo_empresa",))
    x = np.column_stack([np.ones(len(df)), (df.genero == "F").astype(float), df.tempo_empresa])
    beta, *_ = np.linalg.lstsq(x, np.log(df.salario.to_numpy()), rcond=None)
    assert r.coeficientes["coeficiente"].to_numpy() == pytest.approx(beta)
    assert r.hiato == pytest.approx((1 - np.exp(beta[1])) * 100)


def test_controlar_por_cargo_reduz_o_hiato_quando_mulheres_estao_nos_cargos_baixos():
    df = simula(hiato_verdadeiro=0.10)
    assert estimar_hiato(df, controles=()).hiato > estimar_hiato(df).hiato + 3


def test_intervalo_fica_mais_largo_com_menos_dados():
    grande = estimar_hiato(simula(n=3000))
    pequeno = estimar_hiato(simula(n=300))
    assert (pequeno.ic_superior - pequeno.ic_inferior) > (grande.ic_superior - grande.ic_inferior)


def test_ignora_controle_cuja_coluna_nao_existe():
    df = simula().drop(columns=["escolaridade"])
    assert estimar_hiato(df).controles == ("cargo", "tempo_empresa")


def test_controle_desconhecido():
    with pytest.raises(ValueError, match="desconhecidos"):
        estimar_hiato(simula(n=200), controles=("idade",))


def test_exige_homens_e_mulheres():
    df = simula(n=200)
    with pytest.raises(ErroDeDados, match="homens e mulheres"):
        estimar_hiato(df[df.genero == "M"])


def test_controles_redundantes_geram_erro_claro():
    df = simula(n=200)
    df["tempo_empresa"] = 5.0  # coluna constante repete o intercepto
    with pytest.raises(ErroDeDados, match="redundantes"):
        estimar_hiato(df)


def test_poucas_linhas_para_muitos_parametros():
    df = pd.DataFrame(
        {
            "genero": list("MFMFMF"),
            "cargo": ["Analista Júnior", "Analista Pleno", "Gerente"] * 2,
            "salario": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "tempo_empresa": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "escolaridade": ["Superior", "Mestrado"] * 3,
        }
    )  # 6 linhas para 6 parâmetros
    with pytest.raises(ErroDeDados, match="Poucas linhas"):
        estimar_hiato(df)


def test_comparar_especificacoes_devolve_tres_linhas_em_ordem():
    tabela = comparar_especificacoes(simula())
    assert len(tabela) == 3
    assert tabela["controles"].tolist() == ["", "tempo_empresa, escolaridade", "cargo, tempo_empresa, escolaridade"]
    assert (tabela["ic_inferior"] < tabela["hiato"]).all() and (tabela["hiato"] < tabela["ic_superior"]).all()


def test_comparar_especificacoes_sem_colunas_opcionais_tem_uma_linha():
    df = simula().drop(columns=["tempo_empresa", "escolaridade", "cargo"])
    assert len(comparar_especificacoes(df)) == 1
