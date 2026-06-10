# ============================================
# sistema_equidade_salarial.py
# Sistema de Monitoramento de Desigualdade Salarial
# ============================================

import pandas as pd
import hashlib
from datetime import datetime
from typing import Dict, List
import os

class Colaborador:
    def __init__(self, nome: str, genero: str, cargo: str, salario: float, tempo_empresa: int = 0, escolaridade: str = ""):
        self.id = hashlib.md5(nome.encode()).hexdigest()[:8]
        self.nome = nome
        self.genero = genero.upper()
        self.cargo = self._normalizar_cargo(cargo)
        self.salario = float(salario)
        self.tempo_empresa = int(tempo_empresa)
        self.escolaridade = escolaridade
    
    def _normalizar_cargo(self, cargo: str) -> str:
        cargo = cargo.lower().strip()
        mapa = {
            'analista trainee': 'Analista Trainee',
            'analista junior': 'Analista Júnior',
            'analista jr': 'Analista Júnior',
            'analista pleno': 'Analista Pleno',
            'analista senior': 'Analista Senior',
            'analista sr': 'Analista Senior',
            'coordenador': 'Coordenador',
            'supervisor': 'Supervisor',
            'gerente': 'Gerente',
            'diretor': 'Diretor',
            'especialista': 'Especialista',
            'consultor': 'Consultor'
        }
        for chave, valor in mapa.items():
            if chave in cargo:
                return valor
        return cargo.title()


class AnalisadorSalarial:
    def __init__(self):
        self.colaboradores: List[Colaborador] = []
    
    def carregar_csv(self, caminho_arquivo: str) -> Dict:
        try:
            if not os.path.exists(caminho_arquivo):
                return {'sucesso': False, 'erro': f'Arquivo {caminho_arquivo} não encontrado'}
            
            df = pd.read_csv(caminho_arquivo, encoding='utf-8')
            
            colunas_necessarias = ['nome', 'genero', 'cargo', 'salario']
            for col in colunas_necessarias:
                if col not in df.columns:
                    return {'sucesso': False, 'erro': f'Coluna {col} não encontrada'}
            
            self.colaboradores = []
            for _, row in df.iterrows():
                colaborador = Colaborador(
                    nome=row['nome'],
                    genero=row['genero'],
                    cargo=row['cargo'],
                    salario=row['salario'],
                    tempo_empresa=row['tempo_empresa'] if 'tempo_empresa' in df.columns else 0,
                    escolaridade=row['escolaridade'] if 'escolaridade' in df.columns else ""
                )
                self.colaboradores.append(colaborador)
            
            return {'sucesso': True, 'total': len(self.colaboradores)}
        except Exception as e:
            return {'sucesso': False, 'erro': str(e)}
    
    def calcular_diferenca_salarial(self, salario_h: float, salario_m: float) -> float:
        if salario_m <= 0 or salario_h <= 0:
            raise ValueError("Salários devem ser positivos")
        return round(((salario_h - salario_m) / salario_m) * 100, 2)
    
    def analisar_por_cargo(self) -> Dict:
        resultado = {}
        cargos = {}
        
        for colab in self.colaboradores:
            if colab.cargo not in cargos:
                cargos[colab.cargo] = {'M': [], 'F': []}
            cargos[colab.cargo][colab.genero].append(colab.salario)
        
        for cargo, dados in cargos.items():
            salarios_m = dados['M']
            salarios_f = dados['F']
            
            media_m = sum(salarios_m) / len(salarios_m) if salarios_m else 0
            media_f = sum(salarios_f) / len(salarios_f) if salarios_f else 0
            
            if media_m > 0 and media_f > 0:
                diferenca = self.calcular_diferenca_salarial(media_m, media_f)
                alerta = diferenca > 5
            else:
                diferenca = None
                alerta = False
            
            resultado[cargo] = {
                'media_homens': round(media_m, 2),
                'media_mulheres': round(media_f, 2),
                'diferenca_percentual': diferenca,
                'total_homens': len(salarios_m),
                'total_mulheres': len(salarios_f),
                'alerta': alerta
            }
        return resultado
    
    def analisar_geral(self) -> Dict:
        salarios_m = [c.salario for c in self.colaboradores if c.genero == 'M']
        salarios_f = [c.salario for c in self.colaboradores if c.genero == 'F']
        
        media_m = sum(salarios_m) / len(salarios_m) if salarios_m else 0
        media_f = sum(salarios_f) / len(salarios_f) if salarios_f else 0
        
        diferenca = self.calcular_diferenca_salarial(media_m, media_f) if media_m > 0 and media_f > 0 else None
        
        return {
            'total_colaboradores': len(self.colaboradores),
            'total_homens': len(salarios_m),
            'total_mulheres': len(salarios_f),
            'media_salarial_homens': round(media_m, 2),
            'media_salarial_mulheres': round(media_f, 2),
            'diferenca_geral_percentual': diferenca,
            'alerta': diferenca > 5 if diferenca else False
        }
    
    def imprimir_relatorio(self):
        if not self.colaboradores:
            print("❌ Nenhum dado carregado!")
            return
        
        geral = self.analisar_geral()
        cargos = self.analisar_por_cargo()
        
        print("=" * 60)
        print("SISTEMA DE MONITORAMENTO DE DESIGUALDADE SALARIAL")
        print("=" * 60)
        
        print(f"\n📊 Total de colaboradores: {geral['total_colaboradores']}")
        print(f"\n📈 ANÁLISE GERAL:")
        print(f"   Homens: {geral['total_homens']} | Mulheres: {geral['total_mulheres']}")
        print(f"   Média salarial homens: R$ {geral['media_salarial_homens']:,.2f}")
        print(f"   Média salarial mulheres: R$ {geral['media_salarial_mulheres']:,.2f}")
        
        if geral['diferenca_geral_percentual']:
            print(f"   Diferença geral: {geral['diferenca_geral_percentual']:.2f}%")
        
        if geral['alerta']:
            print(f"\n⚠️ ALERTA: Desigualdade salarial acima de 5% detectada!")
        else:
            print(f"\n✅ OK: Dentro do tolerável.")
        
        print(f"\n📋 ANÁLISE POR CARGO:")
        for cargo, dados in sorted(cargos.items()):
            print(f"\n   {cargo}:")
            print(f"     Homens: R$ {dados['media_homens']:,.2f} ({dados['total_homens']})")
            print(f"     Mulheres: R$ {dados['media_mulheres']:,.2f} ({dados['total_mulheres']})")
            if dados['diferenca_percentual']:
                simbolo = "⚠️" if dados['alerta'] else "✅"
                print(f"     Diferença: {dados['diferenca_percentual']:.2f}% {simbolo}")
        
        print(f"\n📅 Data da análise: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)


# ============================================
# EXECUÇÃO PRINCIPAL
# ============================================

if __name__ == "__main__":
    analisador = AnalisadorSalarial()
    
    # Tenta carregar o CSV - VERIFIQUE O NOME DO ARQUIVO!
    nome_arquivo = 'dados_exemplo.csv'
    
    print(f"🔍 Procurando arquivo: {nome_arquivo}")
    print(f"📁 Diretório atual: {os.getcwd()}")
    print(f"📁 Arquivos na pasta: {os.listdir('.')}")
    
    resultado = analisador.carregar_csv(nome_arquivo)
    
    if resultado['sucesso']:
        print(f"✅ {resultado['total']} registros carregados com sucesso!")
        print("\n")
        analisador.imprimir_relatorio()
    else:
        print(f"❌ Erro: {resultado['erro']}")
        print("\n💡 Verifique se o arquivo 'dados_exemplo.csv' está na mesma pasta do script.")