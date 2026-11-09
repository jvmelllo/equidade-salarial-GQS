"""Testes da exportação para Excel e da formatação."""

import io

import pandas as pd
from openpyxl import load_workbook

from equidade import analise, modelo
from equidade.exportacao import gerar_relatorio_excel, resumo_como_tabela
from equidade.formatacao import brl, numero, pct


def test_formatacao_brasileira():
    assert pct(13.94) == "13,9%"
    assert pct(5, 0) == "5%"
    assert numero(10731.8) == "10.732"
    assert numero(1234567.891, 2) == "1.234.567,89"
    assert brl(10731.8) == "R$ 10.732"
    assert pct(None) == "—" and pct(float("nan")) == "—" and brl(None) == "—"


def test_resumo_como_tabela_traduz_indicadores(exemplo):
    tabela = resumo_como_tabela(analise.resumo_geral(exemplo))
    assert list(tabela.columns) == ["Indicador", "Valor"]
    assert "Hiato nas médias (%)" in tabela["Indicador"].tolist()
    assert tabela.loc[tabela["Indicador"] == "Hiato acima do limite?", "Valor"].iloc[0] in ("Sim", "Não")


def test_excel_tem_as_tres_abas_e_so_dados_agregados(exemplo):
    resumo = analise.resumo_geral(exemplo)
    por_cargo = analise.analise_por_cargo(exemplo)
    especificacoes = modelo.comparar_especificacoes(exemplo)

    conteudo = gerar_relatorio_excel(resumo, por_cargo, especificacoes)
    planilhas = load_workbook(io.BytesIO(conteudo))
    assert planilhas.sheetnames == ["Resumo", "Por cargo", "Modelo"]

    por_cargo_xlsx = pd.read_excel(io.BytesIO(conteudo), sheet_name="Por cargo")
    assert len(por_cargo_xlsx) == len(por_cargo)
    assert "Cargo" in por_cargo_xlsx.columns
    # nada que identifique alguém: nenhuma coluna de id/nome/salário individual
    todas_colunas = " ".join(
        str(c).lower()
        for aba in planilhas.sheetnames
        for c in pd.read_excel(io.BytesIO(conteudo), sheet_name=aba).columns
    )
    assert "nome" not in todas_colunas and "id" not in todas_colunas.split()
