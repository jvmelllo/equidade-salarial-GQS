# Metodologia

## 1. Hiato bruto

```
hiato = (1 − média salarial das mulheres ÷ média salarial dos homens) × 100
```

Lê-se como "quanto a menos as mulheres ganham em relação aos homens". Valor negativo significa que as mulheres ganham mais. O painel mostra o hiato nas médias e, no resumo, também nas medianas, que são menos sensíveis a salários muito altos.

O hiato é calculado para a base inteira e para cada cargo. O alerta dispara quando o hiato passa do limite (padrão: 5%). Um hiato de exatamente 5% não dispara alerta: a comparação arredonda antes, para evitar que o erro de ponto flutuante (5,000000000000004) vire alerta.

### Tamanho de amostra

Cargos com poucas pessoas dão médias instáveis. Se um dos grupos (homens ou mulheres) tem menos pessoas que o mínimo configurado (padrão: 5), o cargo recebe **Atenção (amostra pequena)** em vez de **Alerta**. Cargos sem homens ou sem mulheres ficam como **Sem comparação**.

O p-valor por cargo (teste t de Welch) aparece como informação. Ao testar vários cargos, alguns resultados "significativos" surgem por acaso, por isso o p-valor não decide o alerta.

## 2. Hiato ajustado

O hiato bruto mistura duas explicações: mulheres ganhando menos **no mesmo** cargo e mulheres concentradas em cargos que pagam menos. Para separar as duas, o projeto estima uma regressão por mínimos quadrados:

```
log(salário) = a + b · mulher + (cargo) + (tempo de empresa) + (escolaridade) + erro
```

- `mulher` vale 1 para mulheres e 0 para homens.
- Cargo e escolaridade entram como variáveis categóricas (a categoria mais baixa da hierarquia é a referência). Tempo de empresa entra em anos.
- O hiato ajustado é `(1 − exp(b)) × 100`: quanto a menos as mulheres ganham que homens com o mesmo cargo, tempo de empresa e escolaridade.
- O intervalo de confiança de 95% usa a distribuição t com `n − k` graus de liberdade.
- Usa-se o log do salário porque as diferenças salariais são proporcionais (10% a menos vale para quem ganha 4 mil e para quem ganha 20 mil). Por isso, o "sem controles" do modelo (diferença entre médias geométricas) pode diferir um pouco do hiato bruto calculado com médias aritméticas.

O painel mostra três especificações lado a lado: sem controles, só com tempo de empresa e escolaridade, e com cargo também. Ver quanto o hiato muda a cada controle é mais informativo do que um único número.

## 3. Como interpretar

- **Hiato ajustado diferente de zero não prova discriminação.** Faltam variáveis que explicam salário (desempenho, área, negociação, histórico de contratação).
- **Controlar por cargo pode esconder desigualdade.** Se as mulheres são promovidas menos, parte do problema está justamente na diferença de cargos, e o hiato ajustado por cargo não a enxerga. Por isso o hiato bruto e o ajustado aparecem juntos.
- **Amostras pequenas** geram intervalos de confiança largos. Um intervalo que inclui zero significa que a base não permite concluir nada.
- O projeto só trata gênero como `M` e `F`, porque é a classificação usada nos relatórios de transparência salarial. Isso deixa de fora outras identidades.

## 4. Dados de exemplo

Não existe base pública com salário por pessoa (os relatórios de transparência salarial do governo são agregados, sem dados individuais), então `data/dados_exemplo.csv` é **fictício**, gerado por `scripts/gerar_dados_exemplo.py` com semente fixa (42). As regras de geração:

- 400 colaboradores em 9 cargos, com mais gente nos níveis iniciais.
- Proporção de mulheres por cargo definida no script (de 55% em Trainee a 22% em Diretor).
- Salário = base do cargo × ruído (log-normal, desvio de 0,10) × (1 + 1,2% por ano de empresa) × fator de escolaridade (1,00 / 1,06 / 1,12).
- Mulheres recebem 5% a 10% menos no mesmo cargo, conforme o cargo (média de 7,0% entre as mulheres da base).

Com isso, dá para conferir se o modelo funciona: o hiato ajustado deve ficar perto dos 7,0% embutidos. Na base de exemplo ele deu 6,3% (IC 95%: 4,4% a 8,3%), e o intervalo contém o valor embutido.
