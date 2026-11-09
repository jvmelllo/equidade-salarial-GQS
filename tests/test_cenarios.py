"""Cenários de ponta a ponta (caixa-preta): do CSV ao relatório, só pela interface pública."""

import io

import pandas as pd
import pytest
from openpyxl import load_workbook

from equidade import analise, modelo
from equidade.dados import ErroDeDados, carregar_dados
from equidade.exportacao import gerar_relatorio_excel
from scripts import gerar_dados_exemplo, gerar_graficos

from .conftest import CSV_EXEMPLO


def test_base_de_exemplo_tem_o_formato_esperado(exemplo):
    assert len(exemplo) == 400
    assert set(exemplo["genero"]) == {"M", "F"}
    assert exemplo["salario"].min() > 0


def test_fluxo_completo_com_a_base_de_exemplo(exemplo):
    resumo = analise.resumo_geral(exemplo)
    por_cargo = analise.analise_por_cargo(exemplo)
    especificacoes = modelo.comparar_especificacoes(exemplo)

    # hiato bruto grande, e o alerta dispara
    assert 10 < resumo["hiato_medias"] < 20
    assert resumo["alerta"] is True
    # parte do hiato vem da composição por cargo; o que sobra fica perto do embutido (5% a 10%)
    completo = especificacoes.iloc[-1]
    assert completo["ic_inferior"] < 7.5 < completo["ic_superior"]
    assert completo["hiato"] < especificacoes.iloc[0]["hiato"] - 4
    # a participação feminina cai com a senioridade
    assert por_cargo["pct_mulheres"].iloc[0] > por_cargo["pct_mulheres"].iloc[-2]

    planilha = load_workbook(io.BytesIO(gerar_relatorio_excel(resumo, por_cargo, especificacoes)))
    assert planilha["Resumo"].max_row > 5


def test_gerador_e_reprodutivel_e_bate_com_o_arquivo_versionado():
    pd.testing.assert_frame_equal(gerar_dados_exemplo.gerar_dados(), pd.read_csv(CSV_EXEMPLO))


def test_gerador_com_outra_semente_gera_outra_base():
    assert not gerar_dados_exemplo.gerar_dados(semente=1).equals(gerar_dados_exemplo.gerar_dados(semente=2))


def test_script_de_dados_grava_o_csv(tmp_path):
    destino = gerar_dados_exemplo.main(tmp_path / "novo" / "base.csv")
    assert len(carregar_dados(destino)) == 400


def test_script_de_graficos_grava_quatro_pngs(tmp_path):
    caminhos = gerar_graficos.main(tmp_path)
    assert len(caminhos) == 4 and all(c.stat().st_size > 1000 for c in caminhos)


def test_csv_com_problema_gera_mensagem_util_e_nao_traceback():
    csv = io.StringIO("genero,cargo,salario\nF,Gerente,9000\nQ,Gerente,9500\nM,Gerente,abc\n")
    with pytest.raises(ErroDeDados) as erro:
        carregar_dados(csv)
    assert "linha" in str(erro.value)


def test_base_so_com_um_genero_ainda_gera_o_resumo_mas_nao_o_modelo():
    df = carregar_dados(io.StringIO("genero,cargo,salario\nM,Gerente,9000\nM,Gerente,9500\n"))
    assert analise.resumo_geral(df)["hiato_medias"] is None
    assert modelo.comparar_especificacoes(df).empty
