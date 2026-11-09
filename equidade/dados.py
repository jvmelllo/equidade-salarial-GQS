"""Leitura, validação e padronização da base de colaboradores.

Colunas obrigatórias: genero, cargo, salario.
Colunas opcionais usadas na análise: tempo_empresa (anos) e escolaridade.
Qualquer outra coluna (por exemplo, nome ou id) é ignorada de propósito: a
análise não precisa identificar ninguém.
"""

from __future__ import annotations

import csv
import unicodedata

import pandas as pd

COLUNAS_OBRIGATORIAS = ["genero", "cargo", "salario"]
COLUNAS_OPCIONAIS = ["tempo_empresa", "escolaridade"]

# Ordem hierárquica usada nos gráficos e como categoria de referência no modelo.
ORDEM_CARGOS = [
    "Analista Trainee",
    "Analista Júnior",
    "Analista Pleno",
    "Analista Sênior",
    "Especialista",
    "Consultor",
    "Supervisor",
    "Coordenador",
    "Gerente",
    "Diretor",
]
ORDEM_ESCOLARIDADE = ["Ensino Médio", "Superior", "Pós-graduação", "Mestrado", "Doutorado"]

_ALIAS_COLUNAS = {"sexo": "genero", "tempo_de_empresa": "tempo_empresa"}

_GENEROS = {
    "m": "M",
    "masculino": "M",
    "homem": "M",
    "h": "M",
    "f": "F",
    "feminino": "F",
    "mulher": "F",
}

_ESCOLARIDADES = {
    "medio": "Ensino Médio",
    "ensino medio": "Ensino Médio",
    "superior": "Superior",
    "graduacao": "Superior",
    "pos": "Pós-graduação",
    "pos-graduacao": "Pós-graduação",
    "pos graduacao": "Pós-graduação",
    "especializacao": "Pós-graduação",
    "mba": "Pós-graduação",
    "mestrado": "Mestrado",
    "doutorado": "Doutorado",
}

# Cargos de gestão e especialização vêm primeiro: "Gerente Sênior" é Gerente, não Analista Sênior.
_CARGOS_FIXOS = [
    ("diretor", "Diretor"),
    ("gerente", "Gerente"),
    ("coordenador", "Coordenador"),
    ("supervisor", "Supervisor"),
    ("especialista", "Especialista"),
    ("consultor", "Consultor"),
]
_NIVEIS_ANALISTA = [
    ({"trainee"}, "Analista Trainee"),
    ({"junior", "jr"}, "Analista Júnior"),
    ({"pleno", "pl"}, "Analista Pleno"),
    ({"senior", "sr"}, "Analista Sênior"),
]


class ErroDeDados(ValueError):
    """A base enviada tem algum problema que impede a análise."""


def _sem_acento(texto: str) -> str:
    decomposto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def _chave(valor) -> str:
    """Texto em minúsculas, sem acento e sem espaços repetidos (para comparar)."""
    return " ".join(_sem_acento(str(valor)).lower().split())


def normalizar_cargo(cargo) -> str:
    """Padroniza o nome do cargo. Cargos desconhecidos só ganham capitalização."""
    palavras = set(_chave(cargo).split())
    for palavra, nome in _CARGOS_FIXOS:
        if palavra in palavras:
            return nome
    if "analista" in palavras:
        for variantes, nome in _NIVEIS_ANALISTA:
            if palavras & variantes:
                return nome
        return "Analista"
    return " ".join(str(cargo).split()).title()


def normalizar_genero(valor) -> str | None:
    """Devolve 'M', 'F' ou None quando o valor não é reconhecido."""
    return _GENEROS.get(_chave(valor))


def normalizar_escolaridade(valor) -> str:
    chave = _chave(valor)
    return _ESCOLARIDADES.get(chave, " ".join(str(valor).split()).title())


def _ordenar(valores, ordem: list[str]) -> list[str]:
    unicos = list(dict.fromkeys(valores))
    conhecidos = [v for v in ordem if v in unicos]
    desconhecidos = sorted(v for v in unicos if v not in ordem)
    return conhecidos + desconhecidos


def ordenar_cargos(cargos) -> list[str]:
    """Cargos na ordem hierárquica; os desconhecidos vão para o fim, em ordem alfabética."""
    return _ordenar(cargos, ORDEM_CARGOS)


def ordenar_escolaridades(escolaridades) -> list[str]:
    return _ordenar(escolaridades, ORDEM_ESCOLARIDADE)


def _para_numero(serie: pd.Series) -> pd.Series:
    """Converte para número aceitando 'R$ 3.544,71', '3544,71' e '3544.71'."""
    if pd.api.types.is_numeric_dtype(serie):
        return serie.astype(float)
    texto = serie.astype(str).str.replace(r"[R$\s]", "", regex=True)
    tem_ponto_e_virgula = texto.str.contains(".", regex=False) & texto.str.contains(",", regex=False)
    texto = texto.where(~tem_ponto_e_virgula, texto.str.replace(".", "", regex=False))
    texto = texto.str.replace(",", ".", regex=False)
    return pd.to_numeric(texto, errors="coerce")


def _exigir_nenhuma(mascara: pd.Series, descricao: str) -> None:
    """Levanta ErroDeDados citando as linhas do arquivo (cabeçalho = linha 1)."""
    if not mascara.any():
        return
    linhas = [int(i) + 2 for i in mascara[mascara].index]
    mostradas = ", ".join(str(n) for n in linhas[:5])
    resto = f" e mais {len(linhas) - 5}" if len(linhas) > 5 else ""
    raise ErroDeDados(f"{len(linhas)} linha(s) com {descricao} (linhas {mostradas}{resto}).")


def _padronizar_colunas(bruto: pd.DataFrame) -> pd.DataFrame:
    novos_nomes = {}
    for coluna in bruto.columns:
        nome = _chave(coluna).replace(" ", "_")
        novos_nomes[coluna] = _ALIAS_COLUNAS.get(nome, nome)
    return bruto.rename(columns=novos_nomes)


def validar_dados(bruto: pd.DataFrame) -> pd.DataFrame:
    """Valida e padroniza uma tabela já lida. Devolve só as colunas conhecidas."""
    df = _padronizar_colunas(bruto).reset_index(drop=True)

    faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in df.columns]
    if faltando:
        raise ErroDeDados(
            f"Colunas obrigatórias ausentes: {', '.join(faltando)}. "
            f"Colunas encontradas: {', '.join(map(str, df.columns))}."
        )
    if df.empty:
        raise ErroDeDados("O arquivo não tem nenhuma linha de dados.")

    colunas = COLUNAS_OBRIGATORIAS + [c for c in COLUNAS_OPCIONAIS if c in df.columns]
    df = df[colunas].copy()

    df["genero"] = df["genero"].map(normalizar_genero)
    _exigir_nenhuma(df["genero"].isna(), "gênero inválido (use M ou F)")

    cargo_vazio = df["cargo"].isna() | (df["cargo"].astype(str).str.strip() == "")
    _exigir_nenhuma(cargo_vazio, "cargo vazio")
    df["cargo"] = df["cargo"].map(normalizar_cargo)

    df["salario"] = _para_numero(df["salario"])
    _exigir_nenhuma(df["salario"].isna(), "salário ausente ou não numérico")
    _exigir_nenhuma(df["salario"] <= 0, "salário zero ou negativo")

    if "tempo_empresa" in df.columns:
        df["tempo_empresa"] = _para_numero(df["tempo_empresa"])
        _exigir_nenhuma(df["tempo_empresa"].isna(), "tempo de empresa ausente ou não numérico")
        _exigir_nenhuma(df["tempo_empresa"] < 0, "tempo de empresa negativo")

    if "escolaridade" in df.columns:
        vazia = df["escolaridade"].isna() | (df["escolaridade"].astype(str).str.strip() == "")
        _exigir_nenhuma(vazia, "escolaridade vazia")
        df["escolaridade"] = df["escolaridade"].map(normalizar_escolaridade)

    return df


def carregar_dados(origem) -> pd.DataFrame:
    """Lê um CSV (caminho ou arquivo aberto) e devolve a base validada.

    Aceita separador vírgula ou ponto e vírgula e salários como '3544,71'.
    """
    if hasattr(origem, "seek"):
        origem.seek(0)  # arquivos enviados no painel são relidos a cada interação
    try:
        bruto = pd.read_csv(origem, sep=None, engine="python", encoding="utf-8-sig")
    except FileNotFoundError as erro:
        raise ErroDeDados(f"Arquivo não encontrado: {origem}") from erro
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError, csv.Error) as erro:
        raise ErroDeDados(f"Não foi possível ler o CSV: {erro}") from erro
    return validar_dados(bruto)
