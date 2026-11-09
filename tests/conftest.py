from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
CSV_EXEMPLO = RAIZ / "data" / "dados_exemplo.csv"


@pytest.fixture
def exemplo() -> pd.DataFrame:
    from equidade.dados import carregar_dados

    return carregar_dados(CSV_EXEMPLO)


def monta_base(linhas) -> pd.DataFrame:
    """Cria uma base já validada a partir de (genero, cargo, salario)."""
    from equidade.dados import validar_dados

    return validar_dados(pd.DataFrame(linhas, columns=["genero", "cargo", "salario"]))


@pytest.fixture
def csv_valido(tmp_path):
    caminho = tmp_path / "base.csv"
    caminho.write_text(
        "nome,genero,cargo,salario,tempo_empresa,escolaridade\n"
        "Ana,F,analista jr,4000,2,Superior\n"
        "João,M,Analista Junior,4500,3,Pós\n",
        encoding="utf-8",
    )
    return caminho
