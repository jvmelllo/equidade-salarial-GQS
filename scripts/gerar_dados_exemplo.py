"""Gera uma base FICTÍCIA de colaboradores para demonstrar o projeto.

Uso (na pasta do projeto):  python -m scripts.gerar_dados_exemplo

Como os dados são sintéticos, as regras de geração ficam explícitas aqui:
- A pirâmide de cargos tem mais gente nos níveis iniciais.
- A proporção de mulheres cai com a senioridade (22% em Diretor, 55% em Trainee).
- O salário sobe com o cargo, o tempo de empresa (1,2% ao ano) e a escolaridade.
- Mulheres recebem, no mesmo cargo, de 5% a 10% menos (a "penalidade" embutida).
  É esse número que o hiato ajustado do modelo deve conseguir recuperar.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# cargo: (peso na base, proporção de mulheres, salário-base, anos médios de casa, penalidade feminina)
CARGOS = {
    "Analista Trainee": (0.08, 0.55, 3000, 0.8, 0.05),
    "Analista Júnior": (0.20, 0.52, 4500, 2.0, 0.05),
    "Analista Pleno": (0.22, 0.48, 6500, 4.5, 0.07),
    "Analista Sênior": (0.16, 0.42, 9000, 7.0, 0.07),
    "Especialista": (0.07, 0.40, 12000, 9.0, 0.08),
    "Supervisor": (0.09, 0.38, 9500, 8.0, 0.08),
    "Coordenador": (0.08, 0.35, 11500, 10.0, 0.09),
    "Gerente": (0.07, 0.30, 15000, 12.0, 0.10),
    "Diretor": (0.03, 0.22, 22000, 15.0, 0.10),
}

ESCOLARIDADES = ["Superior", "Pós-graduação", "Mestrado"]
FATOR_ESCOLARIDADE = {"Superior": 1.00, "Pós-graduação": 1.06, "Mestrado": 1.12}
PROBABILIDADE_ESCOLARIDADE = {  # Superior, Pós-graduação, Mestrado
    "Analista Trainee": (0.85, 0.13, 0.02),
    "Analista Júnior": (0.78, 0.19, 0.03),
    "Analista Pleno": (0.65, 0.28, 0.07),
    "Analista Sênior": (0.52, 0.35, 0.13),
    "Especialista": (0.35, 0.40, 0.25),
    "Supervisor": (0.50, 0.38, 0.12),
    "Coordenador": (0.42, 0.40, 0.18),
    "Gerente": (0.35, 0.42, 0.23),
    "Diretor": (0.25, 0.45, 0.30),
}
BONUS_POR_ANO = 0.012
RUIDO = 0.10  # desvio-padrão do ruído no log do salário

CAMINHO_PADRAO = Path(__file__).resolve().parents[1] / "data" / "dados_exemplo.csv"


def gerar_dados(n: int = 400, semente: int = 42) -> pd.DataFrame:
    """Gera `n` colaboradores fictícios. A mesma semente gera sempre a mesma base."""
    rng = np.random.default_rng(semente)
    nomes_cargos = list(CARGOS)
    pesos = np.array([CARGOS[c][0] for c in nomes_cargos])

    linhas = []
    for i in range(n):
        cargo = nomes_cargos[rng.choice(len(nomes_cargos), p=pesos / pesos.sum())]
        _, prob_mulher, base, anos_medios, penalidade = CARGOS[cargo]
        genero = "F" if rng.random() < prob_mulher else "M"
        tempo = int(np.clip(round(rng.gamma(shape=3, scale=anos_medios / 3)), 0, 30))
        escolaridade = ESCOLARIDADES[rng.choice(3, p=PROBABILIDADE_ESCOLARIDADE[cargo])]
        salario = (
            base
            * np.exp(rng.normal(0, RUIDO))
            * (1 + BONUS_POR_ANO * tempo)
            * FATOR_ESCOLARIDADE[escolaridade]
            * ((1 - penalidade) if genero == "F" else 1)
        )
        linhas.append(
            {
                "id": f"E{i + 1:04d}",
                "genero": genero,
                "cargo": cargo,
                "salario": round(float(salario), 2),
                "tempo_empresa": tempo,
                "escolaridade": escolaridade,
            }
        )
    return pd.DataFrame(linhas)


def main(destino: Path | None = None) -> Path:
    destino = Path(destino) if destino else CAMINHO_PADRAO
    destino.parent.mkdir(parents=True, exist_ok=True)
    df = gerar_dados()
    df.to_csv(destino, index=False, encoding="utf-8")
    print(f"{len(df)} colaboradores fictícios gravados em {destino}")
    return destino


if __name__ == "__main__":
    main()
