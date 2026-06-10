# gerar_dados_completo.py
import pandas as pd
import random

random.seed(42)

# Nomes
nomes_masculinos = [
    'João Santos', 'Pedro Costa', 'Lucas Lima', 'Rafael Alves', 'Gustavo Pereira',
    'Felipe Nunes', 'Bruno Dias', 'Carlos Mendes', 'André Rocha', 'Marcos Souza',
    'Thiago Oliveira', 'Rodrigo Ferreira', 'Eduardo Gomes', 'Daniel Lima', 'Alexandre Castro',
    'Paulo Henrique', 'Ricardo Martins', 'Fernando Rocha', 'Marcelo Castro', 'Wagner Souza',
    'Diego Alves', 'Leandro Nunes', 'Renato Lima', 'César Mendes', 'Igor Cardoso'
]

nomes_femininos = [
    'Ana Silva', 'Maria Oliveira', 'Carla Souza', 'Fernanda Costa', 'Juliana Lima',
    'Camila Pereira', 'Roberta Alves', 'Beatriz Santos', 'Amanda Rocha', 'Larissa Ferreira',
    'Carolina Barbosa', 'Letícia Gomes', 'Mariana Ribeiro', 'Vanessa Carvalho', 'Tatiane Dias',
    'Cláudia Rocha', 'Renata Martins', 'Tatiane Alves', 'Vanessa Nunes', 'Luana Mendes',
    'Natália Cardoso', 'Laís Oliveira', 'Jéssica Costa', 'Luciana Ferreira', 'Michele Dias'
]

cargos_niveis = {
    'Analista Trainee': (2500, 4000),
    'Analista Júnior': (3800, 5500),
    'Analista Pleno': (5000, 8000),
    'Analista Senior': (7500, 11000),
    'Coordenador': (9000, 14000),
    'Supervisor': (7000, 12000),
    'Gerente': (12000, 18000),
    'Diretor': (18000, 26000),
    'Especialista': (10000, 16000),
}

def salario_com_viés(base_min, base_max, genero, cargo):
    salario_base = random.uniform(base_min, base_max)
    if genero == 'F':
        if 'Diretor' in cargo or 'Gerente' in cargo:
            vies = random.uniform(0.12, 0.28)
        elif 'Senior' in cargo or 'Especialista' in cargo:
            vies = random.uniform(0.08, 0.20)
        else:
            vies = random.uniform(0.05, 0.15)
        return round(salario_base * (1 - vies), 2)
    else:
        bonus = random.uniform(0, 0.08)
        return round(salario_base * (1 + bonus), 2)

dados = []
cargos_lista = list(cargos_niveis.keys())

# Gerar 40 mulheres e 35 homens (total 75)
for i in range(40):
    nome = random.choice(nomes_femininos)
    cargo = random.choice(cargos_lista)
    min_sal, max_sal = cargos_niveis[cargo]
    salario = salario_com_viés(min_sal, max_sal, 'F', cargo)
    dados.append({
        'nome': nome,
        'genero': 'F',
        'cargo': cargo,
        'salario': salario,
        'tempo_empresa': random.randint(0, 18),
        'escolaridade': random.choice(['Superior', 'Pós-graduação', 'Mestrado'])
    })

for i in range(35):
    nome = random.choice(nomes_masculinos)
    cargo = random.choice(cargos_lista)
    min_sal, max_sal = cargos_niveis[cargo]
    salario = salario_com_viés(min_sal, max_sal, 'M', cargo)
    dados.append({
        'nome': nome,
        'genero': 'M',
        'cargo': cargo,
        'salario': salario,
        'tempo_empresa': random.randint(0, 18),
        'escolaridade': random.choice(['Superior', 'Pós-graduação', 'Mestrado'])
    })

df = pd.DataFrame(dados)
df.to_csv('dados_exemplo.csv', index=False, encoding='utf-8')

print("=" * 60)
print("✅ ARQUIVO GERADO COM SUCESSO!")
print("=" * 60)
print(f"📊 Total de registros: {len(df)}")
print(f"   Homens: {len(df[df['genero'] == 'M'])}")
print(f"   Mulheres: {len(df[df['genero'] == 'F'])}")

media_h = df[df['genero'] == 'M']['salario'].mean()
media_m = df[df['genero'] == 'F']['salario'].mean()
print(f"\n📈 Média salarial:")
print(f"   Homens: R$ {media_h:,.2f}")
print(f"   Mulheres: R$ {media_m:,.2f}")
print(f"   Diferença: {((media_h - media_m) / media_m * 100):.1f}%")
print("=" * 60)