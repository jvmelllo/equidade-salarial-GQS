# ============================================
# test_sistema_equidade.py
# Testes unitários, integração, caixa branca e preta
# ============================================

import pytest
import pandas as pd
import tempfile
import os
from sistema_equidade_salarial import Colaborador, AnalisadorSalarial

# ============================================
# TESTES UNITÁRIOS (Caixa Branca)
# ============================================

class TestColaborador:
    
    def test_criar_colaborador(self):
        """Teste unitário: criar um colaborador"""
        colab = Colaborador("João Silva", "M", "Analista", 5000, 3, "Superior")
        assert colab.nome == "João Silva"
        assert colab.genero == "M"
        assert colab.salario == 5000
        assert colab.tempo_empresa == 3
    
    def test_normalizacao_cargo(self):
        """Teste unitário: normalização de cargos (caixa branca)"""
        colab = Colaborador("Teste", "F", "analista pleno", 5000, 2, "Superior")
        assert colab.cargo == "Analista Pleno"
        
        colab2 = Colaborador("Teste2", "M", "analista sr", 6000, 3, "Superior")
        assert colab2.cargo == "Analista Senior"
    
    def test_anonimizacao_id(self):
        """Teste unitário: anonimização do ID"""
        colab1 = Colaborador("João", "M", "Analista", 5000, 2, "Superior")
        colab2 = Colaborador("Maria", "F", "Analista", 5000, 2, "Superior")
        assert colab1.id != colab2.id


class TestAnalisadorSalarial:
    
    def test_calcular_diferenca_normal(self):
        """Teste unitário: cálculo correto da diferença"""
        analisador = AnalisadorSalarial()
        resultado = analisador.calcular_diferenca_salarial(6000, 5000)
        assert resultado == 20.0  # 20% de diferença
    
    def test_calcular_diferenca_igual(self):
        """Teste unitário: salários iguais"""
        analisador = AnalisadorSalarial()
        resultado = analisador.calcular_diferenca_salarial(5000, 5000)
        assert resultado == 0.0
    
    def test_calcular_diferenca_mulher_maior(self):
        """Teste unitário: mulher ganha mais"""
        analisador = AnalisadorSalarial()
        resultado = analisador.calcular_diferenca_salarial(4000, 5000)
        assert resultado == -20.0  # -20% significa mulher ganha mais
    
    def test_calcular_diferenca_valor_negativo(self):
        """Teste unitário: valor negativo deve gerar erro"""
        analisador = AnalisadorSalarial()
        with pytest.raises(ValueError):
            analisador.calcular_diferenca_salarial(-100, 5000)
    
    def test_carregar_csv_sucesso(self):
        """Teste unitário: carregar CSV válido"""
        # Cria arquivo temporário
        df = pd.DataFrame({
            'nome': ['Ana', 'João'],
            'genero': ['F', 'M'],
            'cargo': ['Analista', 'Analista'],
            'salario': [5000, 6000],
            'tempo_empresa': [2, 3],
            'escolaridade': ['Superior', 'Superior']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            df.to_csv(tmp.name, index=False)
            tmp_path = tmp.name
        
        analisador = AnalisadorSalarial()
        resultado = analisador.carregar_csv(tmp_path)
        
        assert resultado['sucesso'] == True
        assert resultado['total'] == 2
        
        os.unlink(tmp_path)
    
    def test_carregar_csv_arquivo_inexistente(self):
        """Teste unitário: arquivo não encontrado"""
        analisador = AnalisadorSalarial()
        resultado = analisador.carregar_csv('arquivo_inexistente.csv')
        assert resultado['sucesso'] == False
        assert 'não encontrado' in resultado['erro'].lower()


# ============================================
# TESTES DE INTEGRAÇÃO (Caixa Branca)
# ============================================

class TestIntegracao:
    
    def setup_method(self):
        """Prepara dados de teste"""
        self.dados_teste = pd.DataFrame({
            'nome': ['Ana', 'João', 'Maria', 'Pedro', 'Carla'],
            'genero': ['F', 'M', 'F', 'M', 'F'],
            'cargo': ['Analista', 'Analista', 'Coordenador', 'Coordenador', 'Analista Senior'],
            'salario': [5000, 6500, 12000, 12500, 8500],
            'tempo_empresa': [2, 3, 5, 4, 3],
            'escolaridade': ['Superior', 'Superior', 'Pós', 'Pós', 'Superior']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            self.dados_teste.to_csv(tmp.name, index=False)
            self.csv_path = tmp.name
    
    def teardown_method(self):
        os.unlink(self.csv_path)
    
    def test_integracao_carga_e_analise_geral(self):
        """Teste de integração: carregar CSV + analisar geral"""
        analisador = AnalisadorSalarial()
        
        # Etapa 1: Carregar
        carga = analisador.carregar_csv(self.csv_path)
        assert carga['sucesso'] == True
        
        # Etapa 2: Analisar geral
        analise = analisador.analisar_geral()
        assert analise['total_colaboradores'] == 5
        assert analise['total_homens'] == 2
        assert analise['total_mulheres'] == 3
    
    def test_integracao_carga_e_analise_por_cargo(self):
        """Teste de integração: carregar CSV + analisar por cargo"""
        analisador = AnalisadorSalarial()
        
        carga = analisador.carregar_csv(self.csv_path)
        assert carga['sucesso'] == True
        
        analise = analisador.analisar_por_cargo()
        assert 'Analista' in analise
        assert 'Coordenador' in analise
    
    def test_integracao_completa_calculo_diferenca(self):
        """Teste de integração: fluxo completo até cálculo de diferença"""
        analisador = AnalisadorSalarial()
        analisador.carregar_csv(self.csv_path)
        
        resultado = analisador.gerar_relatorio()
        
        assert resultado['analise_geral']['diferenca_geral_percentual'] is not None
        assert resultado['total_analisado'] == 5


# ============================================
# TESTES DE SISTEMA (Caixa Preta)
# ============================================

class TestSistemaCaixaPreta:
    
    def setup_method(self):
        self.analisador = AnalisadorSalarial()
    
    def test_cenario_entrada_valida_caso1(self):
        """Cenário 1: CSV com dados corretos e cargos equivalentes"""
        df = pd.DataFrame({
            'nome': ['Ana', 'João', 'Maria', 'Pedro'],
            'genero': ['F', 'M', 'F', 'M'],
            'cargo': ['Analista', 'Analista', 'Analista', 'Analista'],
            'salario': [5000, 6000, 5200, 5800],
            'tempo_empresa': [2, 2, 2, 2],
            'escolaridade': ['Superior', 'Superior', 'Superior', 'Superior']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            df.to_csv(tmp.name, index=False)
            tmp_path = tmp.name
        
        resultado = self.analisador.carregar_csv(tmp_path)
        assert resultado['sucesso'] == True
        
        analise = self.analisador.analisar_geral()
        # Espera-se diferença (média homens 5900, mulheres 5100)
        assert analise['diferenca_geral_percentual'] is not None
        
        os.unlink(tmp_path)
    
    def test_cenario_sem_dados_femininos(self):
        """Cenário 2: Apenas colaboradores homens"""
        df = pd.DataFrame({
            'nome': ['João', 'Pedro', 'Carlos'],
            'genero': ['M', 'M', 'M'],
            'cargo': ['Analista', 'Analista', 'Analista'],
            'salario': [5000, 6000, 5500],
            'tempo_empresa': [2, 3, 2],
            'escolaridade': ['Superior', 'Superior', 'Superior']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            df.to_csv(tmp.name, index=False)
            tmp_path = tmp.name
        
        resultado = self.analisador.carregar_csv(tmp_path)
        analise = self.analisador.analisar_geral()
        
        assert analise['total_mulheres'] == 0
        assert analise['diferenca_geral_percentual'] is None or analise['diferenca_geral_percentual'] == 0
        
        os.unlink(tmp_path)
    
    def test_cenario_csv_mal_formatado(self):
        """Cenário 3: CSV sem coluna obrigatória"""
        df = pd.DataFrame({
            'nome': ['Ana', 'João'],
            'salario': [5000, 6000]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            df.to_csv(tmp.name, index=False)
            tmp_path = tmp.name
        
        resultado = self.analisador.carregar_csv(tmp_path)
        assert resultado['sucesso'] == False
        assert 'Coluna' in resultado['erro']
        
        os.unlink(tmp_path)
    
    def test_cenario_dados_inconsistentes_valor_negativo(self):
        """Cenário 4: Salário negativo"""
        df = pd.DataFrame({
            'nome': ['Ana', 'João'],
            'genero': ['F', 'M'],
            'cargo': ['Analista', 'Analista'],
            'salario': [-1000, 5000],
            'tempo_empresa': [2, 2],
            'escolaridade': ['Superior', 'Superior']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            df.to_csv(tmp.name, index=False)
            tmp_path = tmp.name
        
        # Deve falhar no cálculo, não no carregamento
        self.analisador.carregar_csv(tmp_path)
        
        with pytest.raises(ValueError):
            self.analisador.analisar_geral()
        
        os.unlink(tmp_path)


# ============================================
# TESTES DE CAIXA BRANCA (Estrutura Interna)
# ============================================

class TestCaixaBranca:
    """Testes que verificam a estrutura interna do código"""
    
    def test_fluxo_normalizacao_cargo(self):
        """Verifica todos os caminhos da função _normalizar_cargo"""
        analisador = AnalisadorSalarial()
        
        casos_teste = [
            ('analista', 'Analista'),
            ('Analista Pleno', 'Analista Pleno'),
            ('analista pleno', 'Analista Pleno'),
            ('coordenador', 'Coordenador'),
            ('gerente', 'Gerente'),
            ('cargo desconhecido', 'Cargo Desconhecido')
        ]
        
        # Método de caixa branca: testa cada branch do código
        for entrada, esperado in casos_teste:
            from sistema_equidade_salarial import Colaborador
            colab = Colaborador("Teste", "M", entrada, 5000, 2, "Superior")
            assert colab.cargo == esperado
    
    def test_loop_carregar_csv(self):
        """Verifica se o loop de carregamento processa todos os registros"""
        df = pd.DataFrame({
            'nome': [f'Pessoa{i}' for i in range(10)],
            'genero': ['F' if i % 2 == 0 else 'M' for i in range(10)],
            'cargo': ['Analista'] * 10,
            'salario': [5000] * 10,
            'tempo_empresa': [2] * 10,
            'escolaridade': ['Superior'] * 10
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            df.to_csv(tmp.name, index=False)
            tmp_path = tmp.name
        
        analisador = AnalisadorSalarial()
        resultado = analisador.carregar_csv(tmp_path)
        
        assert resultado['total'] == 10
        os.unlink(tmp_path)
    
    def test_condicional_alerta(self):
        """Testa a condição de alerta (diferença > 5%)"""
        analisador = AnalisadorSalarial()
        
        # Condição verdadeira
        analisador.colaboradores = []
        for _ in range(2):
            analisador.colaboradores.append(Colaborador("H", "M", "Analista", 6000, 2, "Superior"))
            analisador.colaboradores.append(Colaborador("M", "F", "Analista", 5000, 2, "Superior"))
        
        alerta = analisador.analisar_geral()['alerta']
        assert alerta == True  # Diferença de 20% > 5%


# ============================================
# EXECUTAR TODOS OS TESTES
# ============================================

if __name__ == "__main__":
    # Executa com pytest
    pytest.main([__file__, '-v', '--cov=.', '--cov-report=term'])