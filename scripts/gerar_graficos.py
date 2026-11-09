"""Gera os gráficos do README em docs/img (a partir dos dados de exemplo).

Uso (na pasta do projeto):  python -m scripts.gerar_graficos
"""

from __future__ import annotations

from pathlib import Path

from equidade import analise, graficos, modelo
from equidade.dados import carregar_dados

RAIZ = Path(__file__).resolve().parents[1]


def main(destino: Path | None = None) -> list[Path]:
    destino = Path(destino) if destino else RAIZ / "docs" / "img"
    destino.mkdir(parents=True, exist_ok=True)

    df = carregar_dados(RAIZ / "data" / "dados_exemplo.csv")
    por_cargo = analise.analise_por_cargo(df)
    especificacoes = modelo.comparar_especificacoes(df)

    figuras = {
        "hiato_por_cargo.png": graficos.grafico_hiato_por_cargo(
            por_cargo, analise.LIMITE_ALERTA_PADRAO, analise.N_MINIMO_PADRAO
        ),
        "medias_por_cargo.png": graficos.grafico_medias_por_cargo(por_cargo),
        "participacao_feminina.png": graficos.grafico_representacao(por_cargo),
        "hiato_ajustado.png": graficos.grafico_especificacoes(especificacoes),
    }
    caminhos = []
    for nome, fig in figuras.items():
        caminho = destino / nome
        graficos.salvar(fig, caminho)
        caminhos.append(caminho)
        print(f"gravado: {caminho}")
    return caminhos


if __name__ == "__main__":
    main()
