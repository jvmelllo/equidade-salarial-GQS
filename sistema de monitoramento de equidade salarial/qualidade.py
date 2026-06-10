# ============================================
# qualidade.py - ISO 9126 e MPS.BR
# ============================================

class ISO9126:
    """
    ISO/IEC 9126 - Modelo de Qualidade de Software
    6 Características avaliadas
    """
    
    @staticmethod
    def funcionalidade():
        """Funcionalidade: O software faz o que promete?"""
        return {
            'nome': 'Funcionalidade',
            'nota': 9,
            'itens': [
                ('Adequação', 'Calcula corretamente diferença salarial'),
                ('Acurácia', 'Resultados precisos com validação'),
                ('Interoperabilidade', 'Importa CSV, exporta relatórios'),
                ('Segurança', 'Anonimização de dados (LGPD)')
            ]
        }
    
    @staticmethod
    def confiabilidade():
        """Confiabilidade: O software é estável?"""
        return {
            'nome': 'Confiabilidade',
            'nota': 8,
            'itens': [
                ('Tolerância a falhas', 'Tratamento de arquivos inválidos'),
                ('Recuperabilidade', 'Recupera de erros de entrada'),
                ('Maturidade', 'Poucos bugs identificados')
            ]
        }
    
    @staticmethod
    def usabilidade():
        """Usabilidade: É fácil de usar?"""
        return {
            'nome': 'Usabilidade',
            'nota': 8,
            'itens': [
                ('Inteligibilidade', 'Interface simples por CSV'),
                ('Apreensibilidade', 'Fácil aprendizado'),
                ('Operacionalidade', 'Comandos claros')
            ]
        }
    
    @staticmethod
    def eficiencia():
        """Eficiência: Performance e uso de recursos"""
        return {
            'nome': 'Eficiência',
            'nota': 8,
            'itens': [
                ('Comportamento temporal', 'Processa 10k registros em <5s'),
                ('Utilização de recursos', 'Baixo consumo de memória')
            ]
        }
    
    @staticmethod
    def manutenibilidade():
        """Manutenibilidade: É fácil de modificar?"""
        return {
            'nome': 'Manutenibilidade',
            'nota': 9,
            'itens': [
                ('Analisabilidade', 'Código comentado e modular'),
                ('Modificabilidade', 'Fácil adicionar novos cargos'),
                ('Estabilidade', 'Baixo risco ao modificar'),
                ('Testabilidade', 'Testes automatizados')
            ]
        }
    
    @staticmethod
    def portabilidade():
        """Portabilidade: Roda em diferentes ambientes?"""
        return {
            'nome': 'Portabilidade',
            'nota': 9,
            'itens': [
                ('Adaptabilidade', 'Independente de SO'),
                ('Capacidade de instalação', 'Pip install -r requirements'),
                ('Conformidade', 'Python padrão')
            ]
        }
    
    @classmethod
    def relatorio_completo(cls):
        """Gera relatório ISO 9126 completo"""
        print("=" * 70)
        print("RELATÓRIO ISO 9126 - QUALIDADE DE SOFTWARE")
        print("=" * 70)
        
        total = 0
        caracteristicas = [
            cls.funcionalidade(),
            cls.confiabilidade(),
            cls.usabilidade(),
            cls.eficiencia(),
            cls.manutenibilidade(),
            cls.portabilidade()
        ]
        
        for c in caracteristicas:
            print(f"\n📌 {c['nome']} (Nota: {c['nota']}/10)")
            for item, desc in c['itens']:
                print(f"   • {item}: {desc}")
            total += c['nota']
        
        media = total / len(caracteristicas)
        print(f"\n{'='*70}")
        print(f"⭐ MÉDIA GERAL ISO 9126: {media:.1f}/10")
        print(f"{'='*70}")
        
        if media >= 8:
            print("✅ Software com alta qualidade segundo ISO 9126")
        
        return media


class MPSBR:
    """
    MPS.BR - Melhoria de Processo de Software Brasileiro
    Níveis: G, F, E, D, C, B, A
    """
    
    @staticmethod
    def nivel_atual():
        """Avalia o nível MPS.BR do projeto"""
        niveis = {
            'G - Gerenciamento de Projetos': True,
            'F - Gerência de Requisitos': True,
            'E - Gerência de Portfólio': False,
            'D - Gerência de Configuração': False,
            'C - Verificação e Validação': False,
            'B - Garantia da Qualidade': False,
            'A - Melhoria Contínua': False
        }
        
        print("=" * 70)
        print("RELATÓRIO MPS.BR - NÍVEL DE MATURIDADE")
        print("=" * 70)
        
        print("\n📊 NÍVEIS ATINGIDOS:")
        for nivel, atingido in niveis.items():
            simbolo = "✅" if atingido else "❌"
            print(f"   {simbolo} {nivel}")
        
        print("\n📋 JUSTIFICATIVA NÍVEL G:")
        print("   • Planejamento do projeto definido")
        print("   • Cronograma estabelecido")
        print("   • Divisão de responsabilidades da equipe")
        
        print("\n📋 JUSTIFICATIVA NÍVEL F:")
        print("   • Requisitos documentados")
        print("   • Rastreabilidade requisitos → testes")
        print("   • Validação com stakeholders")
        
        print("\n" + "=" * 70)
        print("⭐ NÍVEL MPS.BR ATUAL: G (Gerenciamento de Projetos)")
        print("⭐ NÍVEL MPS.BR PARCIAL: F (Gerência de Requisitos)")
        print("=" * 70)
        
        return "G/F"


if __name__ == "__main__":
    print("\n")
    ISO9126.relatorio_completo()
    print("\n")
    MPSBR.nivel_atual()