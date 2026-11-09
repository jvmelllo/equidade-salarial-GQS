"""Testes unitários da leitura e validação dos dados."""

import io

import pandas as pd
import pytest

from equidade.dados import (
    ErroDeDados,
    carregar_dados,
    normalizar_cargo,
    normalizar_escolaridade,
    normalizar_genero,
    ordenar_cargos,
    validar_dados,
)


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("analista jr", "Analista Júnior"),
        ("Analista Junior", "Analista Júnior"),
        ("ANALISTA SR", "Analista Sênior"),
        ("analista sênior", "Analista Sênior"),
        ("  analista   pleno ", "Analista Pleno"),
        ("Analista Trainee", "Analista Trainee"),
        ("Gerente Sênior", "Gerente"),
        ("coordenador de TI", "Coordenador"),
        ("analista", "Analista"),
        ("desenvolvedor junior", "Desenvolvedor Junior"),
    ],
)
def test_normalizar_cargo(entrada, esperado):
    assert normalizar_cargo(entrada) == esperado


@pytest.mark.parametrize(
    "entrada, esperado",
    [("M", "M"), ("m", "M"), ("Masculino", "M"), ("F", "F"), (" feminino ", "F"),
     ("X", None), (float("nan"), None), ("", None)],
)
def test_normalizar_genero(entrada, esperado):
    assert normalizar_genero(entrada) == esperado


def test_normalizar_escolaridade():
    assert normalizar_escolaridade("pós-graduação") == "Pós-graduação"
    assert normalizar_escolaridade("Pos") == "Pós-graduação"
    assert normalizar_escolaridade("mestrado") == "Mestrado"
    assert normalizar_escolaridade("técnico") == "Técnico"  # desconhecida: só capitaliza


def test_ordenar_cargos_segue_a_hierarquia_e_deixa_desconhecidos_no_fim():
    cargos = ["Gerente", "Zelador", "Analista Júnior", "Diretor", "Auxiliar"]
    assert ordenar_cargos(cargos) == ["Analista Júnior", "Gerente", "Diretor", "Auxiliar", "Zelador"]


def test_carregar_csv_valido(csv_valido):
    df = carregar_dados(csv_valido)
    assert list(df.columns) == ["genero", "cargo", "salario", "tempo_empresa", "escolaridade"]
    assert df["cargo"].tolist() == ["Analista Júnior", "Analista Júnior"]
    assert df["escolaridade"].tolist() == ["Superior", "Pós-graduação"]
    assert "nome" not in df.columns  # a análise não guarda quem é cada pessoa


def test_carregar_csv_ignora_colunas_extras():
    csv = io.StringIO("id,genero,cargo,salario,observacao\nE1,F,Gerente,9000,x\nE2,M,Gerente,9500,y\n")
    df = carregar_dados(csv)
    assert list(df.columns) == ["genero", "cargo", "salario"]


def test_carregar_csv_com_ponto_e_virgula_e_virgula_decimal():
    csv = io.StringIO("Gênero;Cargo;Salário\nF;Gerente;R$ 3.544,71\nM;Gerente;4000,5\n")
    df = carregar_dados(csv)
    assert df["salario"].tolist() == [3544.71, 4000.5]
    assert df["genero"].tolist() == ["F", "M"]


def test_arquivo_inexistente():
    with pytest.raises(ErroDeDados, match="não encontrado"):
        carregar_dados("nao_existe.csv")


def test_arquivo_vazio():
    with pytest.raises(ErroDeDados):
        carregar_dados(io.StringIO(""))


def test_so_cabecalho():
    with pytest.raises(ErroDeDados, match="nenhuma linha"):
        carregar_dados(io.StringIO("genero,cargo,salario\n"))


def test_coluna_obrigatoria_ausente():
    with pytest.raises(ErroDeDados, match="ausentes: salario"):
        validar_dados(pd.DataFrame({"genero": ["F"], "cargo": ["Gerente"]}))


def test_genero_invalido_cita_as_linhas():
    df = pd.DataFrame({"genero": ["F", "X", "M", "Z"], "cargo": ["Gerente"] * 4, "salario": [1, 2, 3, 4]})
    with pytest.raises(ErroDeDados, match=r"2 linha\(s\) com gênero inválido.*linhas 3, 5"):
        validar_dados(df)


def test_salario_negativo_ou_zero():
    df = pd.DataFrame({"genero": ["F", "M"], "cargo": ["Gerente"] * 2, "salario": [-1000, 5000]})
    with pytest.raises(ErroDeDados, match="zero ou negativo"):
        validar_dados(df)


def test_salario_nao_numerico():
    df = pd.DataFrame({"genero": ["F", "M"], "cargo": ["Gerente"] * 2, "salario": ["abc", "5000"]})
    with pytest.raises(ErroDeDados, match="ausente ou não numérico"):
        validar_dados(df)


def test_cargo_vazio():
    df = pd.DataFrame({"genero": ["F", "M"], "cargo": ["Gerente", " "], "salario": [1, 2]})
    with pytest.raises(ErroDeDados, match="cargo vazio"):
        validar_dados(df)


def test_tempo_de_empresa_negativo():
    df = pd.DataFrame({"genero": ["F"], "cargo": ["Gerente"], "salario": [1], "tempo_empresa": [-2]})
    with pytest.raises(ErroDeDados, match="tempo de empresa negativo"):
        validar_dados(df)


def test_arquivo_binario_com_bom_como_o_do_painel_e_relido_do_inicio():
    conteudo = io.BytesIO("﻿genero,cargo,salario\nF,Gerente,9000\nM,Gerente,9500\n".encode("utf-8"))
    primeira = carregar_dados(conteudo)
    segunda = carregar_dados(conteudo)  # o painel relê o mesmo arquivo a cada interação
    pd.testing.assert_frame_equal(primeira, segunda)
    assert len(segunda) == 2
