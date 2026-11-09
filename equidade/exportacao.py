"""Relatório em Excel com os resultados agregados (sem dados individuais)."""

from __future__ import annotations

import io

import pandas as pd

from .analise import COLUNAS_POR_CARGO

_ROTULOS_RESUMO = [
    ("total", "Colaboradores"),
    ("homens", "Homens"),
    ("mulheres", "Mulheres"),
    ("pct_mulheres", "Mulheres na base (%)"),
    ("media_homens", "Salário médio dos homens (R$)"),
    ("media_mulheres", "Salário médio das mulheres (R$)"),
    ("mediana_homens", "Salário mediano dos homens (R$)"),
    ("mediana_mulheres", "Salário mediano das mulheres (R$)"),
    ("hiato_medias", "Hiato nas médias (%)"),
    ("hiato_medianas", "Hiato nas medianas (%)"),
    ("limite", "Limite de alerta (%)"),
    ("alerta", "Hiato acima do limite?"),
]

_ROTULOS_POR_CARGO = {
    "cargo": "Cargo",
    "n_homens": "Homens",
    "n_mulheres": "Mulheres",
    "pct_mulheres": "Mulheres no cargo (%)",
    "media_homens": "Média dos homens (R$)",
    "media_mulheres": "Média das mulheres (R$)",
    "hiato": "Hiato (%)",
    "p_valor": "p-valor (teste t de Welch)",
    "status": "Situação",
}

_ROTULOS_MODELO = {
    "especificacao": "Especificação",
    "controles": "Controles",
    "hiato": "Hiato ajustado (%)",
    "ic_inferior": "IC 95% inferior (%)",
    "ic_superior": "IC 95% superior (%)",
    "p_valor": "p-valor",
    "n": "Observações",
}


def resumo_como_tabela(resumo: dict) -> pd.DataFrame:
    """Transforma o dicionário de resumo_geral em uma tabela Indicador/Valor."""
    linhas = []
    for chave, rotulo in _ROTULOS_RESUMO:
        valor = resumo[chave]
        if isinstance(valor, bool):
            valor = "Sim" if valor else "Não"
        elif isinstance(valor, float):
            valor = round(valor, 2)
        linhas.append({"Indicador": rotulo, "Valor": valor})
    return pd.DataFrame(linhas)


def tabela_por_cargo_legivel(por_cargo: pd.DataFrame) -> pd.DataFrame:
    tabela = por_cargo[COLUNAS_POR_CARGO].reset_index()
    return tabela.rename(columns=_ROTULOS_POR_CARGO).round(
        {"Mulheres no cargo (%)": 1, "Média dos homens (R$)": 2, "Média das mulheres (R$)": 2,
         "Hiato (%)": 2, "p-valor (teste t de Welch)": 4}
    )


def tabela_modelo_legivel(especificacoes: pd.DataFrame) -> pd.DataFrame:
    tabela = especificacoes.rename(columns=_ROTULOS_MODELO)
    return tabela.round(
        {"Hiato ajustado (%)": 2, "IC 95% inferior (%)": 2, "IC 95% superior (%)": 2, "p-valor": 4}
    )


def gerar_relatorio_excel(
    resumo: dict, por_cargo: pd.DataFrame, especificacoes: pd.DataFrame
) -> bytes:
    """Monta o arquivo .xlsx (abas Resumo, Por cargo e Modelo) e devolve os bytes."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as excel:
        resumo_como_tabela(resumo).to_excel(excel, sheet_name="Resumo", index=False)
        tabela_por_cargo_legivel(por_cargo).to_excel(excel, sheet_name="Por cargo", index=False)
        tabela_modelo_legivel(especificacoes).to_excel(excel, sheet_name="Modelo", index=False)
        for planilha in excel.book.worksheets:
            for coluna in planilha.columns:
                largura = max(len(str(celula.value or "")) for celula in coluna)
                planilha.column_dimensions[coluna[0].column_letter].width = min(largura + 2, 45)
    return buffer.getvalue()
