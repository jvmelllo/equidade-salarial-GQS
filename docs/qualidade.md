# Qualidade do software

O projeto nasceu como trabalho final da disciplina de Gestão e Qualidade de Software, em que a qualidade era avaliada pelas seis características da ISO/IEC 9126. Esta página mantém esse eixo, mas aponta evidências que dá para conferir no repositório, em vez de notas.

> A ISO/IEC 9126 foi substituída em 2011 pela ISO/IEC 25010, que mantém a ideia e muda o nome de algumas características. Usei a 9126 por ser a da disciplina.

| Característica | Evidência no projeto |
|---|---|
| **Funcionalidade** | O hiato bruto e o ajustado têm testes de fórmula. O modelo é comparado com o mínimos quadrados do NumPy e recupera um hiato conhecido em dados simulados (`tests/test_modelo.py`). O limite de alerta tem teste no valor exato (5%). |
| **Confiabilidade** | A leitura do CSV valida linha a linha e a mensagem de erro diz quais linhas têm problema. Cargos sem homens ou sem mulheres, bases só com um gênero e controles redundantes têm tratamento e teste (`tests/test_dados.py`, `tests/test_graficos.py`, `tests/test_modelo.py`). |
| **Usabilidade** | O painel explica como ler cada resultado e avisa quando uma comparação não é confiável (amostra pequena). Não houve teste com usuários. |
| **Eficiência** | A suíte inteira (79 testes, incluindo geração de gráficos e do Excel) roda em cerca de 3 segundos. Não há teste de carga com bases grandes. |
| **Manutenibilidade** | Pacote `equidade/` dividido por responsabilidade (dados, análise, modelo, gráficos, exportação), sem estado global; o painel (`app.py`) só orquestra essas funções. |
| **Portabilidade** | Python puro com bibliotecas comuns de dados. Testado só com Python 3.13 e as versões listadas no README; as versões mínimas do `requirements.txt` são estimativas e não foram testadas. O painel (`app.py`) não tem teste automatizado. |

## Tipos de teste

| Arquivo | Tipo | O que cobre |
|---|---|---|
| `tests/test_dados.py` | unitário | normalização de cargo, gênero e escolaridade; validação do CSV |
| `tests/test_analise.py` | unitário | fórmula do hiato, alerta, status por cargo |
| `tests/test_modelo.py` | unitário e de propriedade | regressão contra o NumPy; recuperação de hiato conhecido; erros |
| `tests/test_exportacao.py` | integração | Excel gerado a partir das análises; formatação |
| `tests/test_graficos.py` | integração | geração dos gráficos, inclusive com dados incompletos |
| `tests/test_cenarios.py` | caixa-preta (ponta a ponta) | do CSV ao relatório, só pela interface pública |

## Sobre o MPS.BR

A versão original trazia uma autoavaliação nos níveis do MPS.BR. Ela foi retirada: os níveis do MPS.BR avaliam a maturidade dos processos de uma organização, feita por instituições avaliadoras, e não a qualidade de um projeto individual. A versão original continua no histórico do Git.
