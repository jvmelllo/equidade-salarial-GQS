# ============================================
# qualidade.py - ISO 9126 e MPS.BR
# VERSÃO CORRIGIDA
# ============================================

class ISO9126:
    """
    ISO/IEC 9126 - Modelo de Qualidade de Software
    """
    
    @staticmethod
    def funcionalidade():
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
        return {
            'nome': 'Confiabilidade',
            'nota': 8,
            'itens': [
                ('Tolerância a falhas', 'Tratamento de arquivos inválidos'),
                ('Recuperabilidade', 'Recupera de erros de entrada'),
                ('Maturidade', 'Poucos bugs identificados (2 encontrados)')
            ]
        }
    
    @staticmethod
    def usabilidade():
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
        return {
            'nome': 'Eficiência',
            'nota': 8,
            'itens': [
                ('Comportamento temporal', 'Processa registros rapidamente'),
                ('Utilização de recursos', 'Baixo consumo de memória')
            ]
        }
    
    @staticmethod
    def manutenibilidade():
        return {
            'nome': 'Manutenibilidade',
            'nota': 8,
            'itens': [
                ('Analisabilidade', 'Código comentado e modular'),
                ('Modificabilidade', 'Fácil adicionar novos cargos'),
                ('Estabilidade', 'Baixo risco ao modificar'),
                ('Testabilidade', 'Testes automatizados (19 testes)')
            ]
        }
    
    @staticmethod
    def portabilidade():
        return {
            'nome': 'Portabilidade',
            'nota': 9,
            'itens': [
                ('Adaptabilidade', 'Funciona em Windows, Linux, Mac'),
                ('Capacidade de instalação', 'pip install -r requirements'),
                ('Conformidade', 'Python padrão 3.11+')
            ]
        }
    
    @classmethod
    def relatorio_completo(cls):
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
    """MPS.BR - Níveis G, F, E, D, C, B, A"""
    
    @staticmethod
    def nivel_atual():
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
        
        print("\n📋 JUSTIFICATIVA NÍVEL G (Gerenciamento de Projetos):")
        print("   • Planejamento do projeto definido")
        print("   • Cronograma estabelecido")
        print("   • Divisão de responsabilidades da equipe")
        
        print("\n📋 JUSTIFICATIVA NÍVEL F (Gerência de Requisitos):")
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