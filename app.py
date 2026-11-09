"""Painel interativo do Monitor de Equidade Salarial.

Como rodar (na pasta do projeto):  python -m streamlit run app.py
"""

from pathlib import Path

import streamlit as st

from equidade import analise, graficos, modelo
from equidade.dados import ErroDeDados, carregar_dados
from equidade.exportacao import (
    gerar_relatorio_excel,
    resumo_como_tabela,
    tabela_modelo_legivel,
    tabela_por_cargo_legivel,
)
from equidade.formatacao import numero, pct
from equidade.modelo import CONTROLES_DISPONIVEIS, ROTULOS_CONTROLES

CAMINHO_EXEMPLO = Path(__file__).parent / "data" / "dados_exemplo.csv"

st.set_page_config(page_title="Monitor de Equidade Salarial", page_icon="⚖️", layout="wide")


@st.cache_data
def carregar_exemplo():
    return carregar_dados(CAMINHO_EXEMPLO)


def barra_lateral():
    """Desenha a barra lateral e devolve (arquivo enviado, limite, n mínimo)."""
    with st.sidebar:
        st.header("Dados")
        arquivo = st.file_uploader(
            "Envie um CSV",
            type="csv",
            help="Colunas obrigatórias: genero, cargo, salario. Opcionais: tempo_empresa e escolaridade.",
        )
        st.caption(
            "Sem arquivo, o painel usa dados fictícios. O CSV enviado fica só na memória desta "
            "sessão, mas não envie dados reais em uma demonstração pública."
        )
        st.header("Parâmetros")
        limite = st.slider(
            "Limite de alerta (hiato, %)", 1.0, 20.0, analise.LIMITE_ALERTA_PADRAO, 0.5,
            help="Hiato acima deste valor vira alerta.",
        )
        n_minimo = st.number_input(
            "Mínimo de pessoas por grupo", min_value=2, max_value=50, value=analise.N_MINIMO_PADRAO, step=1,
            help="Cargos com menos pessoas que isso em homens ou em mulheres não geram alerta, só atenção.",
        )
    return arquivo, limite, int(n_minimo)


def escolher_controles(df):
    disponiveis = [c for c in CONTROLES_DISPONIVEIS if c in df.columns]
    with st.sidebar:
        st.header("Hiato ajustado")
        return st.multiselect(
            "Controlar por",
            options=disponiveis,
            default=disponiveis,
            format_func=lambda c: ROTULOS_CONTROLES[c],
            help="Compara homens e mulheres com o mesmo valor destas características.",
        )


def indicadores(resumo, ajustado):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Colaboradores", numero(resumo["total"]))
    c2.metric(
        "Mulheres na base", pct(resumo["pct_mulheres"]),
        help=f"{resumo['mulheres']} mulheres e {resumo['homens']} homens.",
    )
    c3.metric(
        "Hiato bruto (médias)", pct(resumo["hiato_medias"]),
        help="Quanto a menos as mulheres ganham que os homens, comparando as médias de todos. "
             f"Nas medianas: {pct(resumo['hiato_medianas'])}.",
    )
    if ajustado is None:
        c4.metric("Hiato ajustado", "—", help="Não foi possível estimar com os controles escolhidos.")
    else:
        c4.metric(
            "Hiato ajustado", pct(ajustado.hiato),
            help=f"Intervalo de confiança de 95%: {pct(ajustado.ic_inferior)} a {pct(ajustado.ic_superior)}.",
        )


def aba_visao_geral(por_cargo):
    esquerda, direita = st.columns(2)
    with esquerda:
        st.subheader("Participação feminina por cargo")
        st.pyplot(graficos.grafico_representacao(por_cargo, titulo=None))
    with direita:
        st.subheader("Salário médio por cargo")
        st.pyplot(graficos.grafico_medias_por_cargo(por_cargo, titulo=None))
    with st.expander("Ver como tabela"):
        st.dataframe(tabela_por_cargo_legivel(por_cargo))


def aba_por_cargo(por_cargo, limite, n_minimo):
    st.subheader("Hiato salarial por cargo")
    st.caption(
        f"Alerta: hiato acima de {pct(limite, 1)} com pelo menos {n_minimo} pessoas em cada grupo. "
        "Com menos gente a diferença pode ser acaso, então o cargo fica só em atenção."
    )
    st.pyplot(graficos.grafico_hiato_por_cargo(por_cargo, limite, n_minimo, titulo=None))
    st.dataframe(tabela_por_cargo_legivel(por_cargo))
    st.caption(
        "O p-valor é só informativo: ao testar vários cargos, alguns saem 'significativos' por acaso."
    )


def aba_ajustado(especificacoes, ajustado, erro_modelo):
    st.subheader("Hiato ajustado")
    st.markdown(
        "O hiato bruto mistura duas coisas: pessoas que ganham menos **no mesmo** cargo e mulheres "
        "concentradas em cargos que pagam menos. O modelo compara pessoas parecidas e mostra "
        "quanto do hiato sobra. **Sobrar hiato não prova discriminação** (faltam variáveis como "
        "desempenho), e controlar por cargo pode esconder diferenças de promoção."
    )
    if especificacoes.empty:
        st.info("Não foi possível estimar o modelo com esta base (é preciso ter homens e mulheres).")
        return
    st.pyplot(graficos.grafico_especificacoes(especificacoes, titulo=None))
    st.dataframe(tabela_modelo_legivel(especificacoes))
    if erro_modelo:
        st.warning(f"Com os controles escolhidos na barra lateral: {erro_modelo}")
    elif ajustado is not None:
        with st.expander("Coeficientes do modelo escolhido na barra lateral"):
            st.caption(f"R² = {ajustado.r2:.3f} · {ajustado.n} observações · efeito em % sobre o salário.")
            st.dataframe(ajustado.coeficientes.round(4))


def aba_exportacao(df, resumo, por_cargo, especificacoes):
    st.subheader("Relatório e dados")
    st.download_button(
        "Baixar relatório em Excel",
        data=gerar_relatorio_excel(resumo, por_cargo, especificacoes),
        file_name="relatorio_equidade_salarial.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Só resultados agregados, sem dados individuais.",
    )
    st.dataframe(resumo_como_tabela(resumo))
    with st.expander("Ver as primeiras linhas da base usada"):
        st.dataframe(df.head(100))


def main():
    st.title("Monitor de Equidade Salarial")
    st.caption(
        "Compara salários de homens e mulheres: hiato bruto, por cargo e ajustado por "
        "cargo, tempo de empresa e escolaridade."
    )
    arquivo, limite, n_minimo = barra_lateral()

    try:
        df = carregar_exemplo() if arquivo is None else carregar_dados(arquivo)
    except ErroDeDados as erro:
        st.error(f"Não foi possível usar o arquivo: {erro}")
        st.stop()
        return
    if arquivo is None:
        st.info("Você está vendo dados **fictícios** gerados para demonstração.")

    controles = escolher_controles(df)
    resumo = analise.resumo_geral(df, limite)
    por_cargo = analise.analise_por_cargo(df, limite, n_minimo)
    especificacoes = modelo.comparar_especificacoes(df)
    ajustado, erro_modelo = None, ""
    try:
        ajustado = modelo.estimar_hiato(df, tuple(controles))
    except ErroDeDados as erro:
        erro_modelo = str(erro)

    if resumo["alerta"]:
        st.warning(
            f"O hiato bruto ({pct(resumo['hiato_medias'])}) está acima do limite de {pct(limite)}."
        )
    elif resumo["hiato_medias"] is not None:
        st.success(f"O hiato bruto ({pct(resumo['hiato_medias'])}) está dentro do limite de {pct(limite)}.")
    indicadores(resumo, ajustado)

    visao, cargos, ajuste, exportacao = st.tabs(
        ["Visão geral", "Por cargo", "Hiato ajustado", "Relatório e dados"]
    )
    with visao:
        aba_visao_geral(por_cargo)
    with cargos:
        aba_por_cargo(por_cargo, limite, n_minimo)
    with ajuste:
        aba_ajustado(especificacoes, ajustado, erro_modelo)
    with exportacao:
        aba_exportacao(df, resumo, por_cargo, especificacoes)


main()
