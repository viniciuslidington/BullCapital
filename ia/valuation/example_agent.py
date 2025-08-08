"""
Exemplo de uso direto do Agente Financeiro.
Demonstra como usar o agente programaticamente sem API HTTP.
"""

from ia.Agent.financial_agent import agent


def exemplo_chat():
    """Exemplo de chat geral com o agente."""
    
    print("🤖 Exemplo de Chat Geral")
    print("=" * 40)
    
    perguntas = [
        "O que é margem de segurança na análise fundamentalista?",
        "Explique o conceito de valor intrínseco",
        "Quais são os principais indicadores fundamentalistas?",
    ]
    
    for pergunta in perguntas:
        print(f"\n❓ Pergunta: {pergunta}")
        print("-" * 40)
        
        try:
            resposta = agent.chat(pergunta)
            print(f"✅ Resposta: {resposta}")
        except Exception as e:
            print(f"❌ Erro: {e}")


def exemplo_analise_acoes():
    """Exemplo de análise específica de ações."""
    
    print("\n📊 Exemplo de Análise de Ações")
    print("=" * 40)
    
    acoes = [
        ("PETR4", "Analise esta ação e me dê uma recomendação"),
        ("VALE3", "Faça uma análise completa desta ação"),
        ("ITUB4", "Analise os múltiplos e valuation desta ação"),
    ]
    
    for ticker, pergunta in acoes:
        print(f"\n📈 Análise da {ticker}")
        print(f"❓ Pergunta: {pergunta}")
        print("-" * 40)
        
        try:
            analise = agent.analyze_stock(pergunta, ticker)
            print(f"✅ Análise: {analise}")
        except Exception as e:
            print(f"❌ Erro: {e}")


def exemplo_uso_programatico():
    """Exemplo de uso programático do agente."""
    
    print("\n💻 Exemplo de Uso Programático")
    print("=" * 40)
    
    # Criar uma função que usa o agente
    def analisar_portfolio(acoes):
        """Analisa um portfolio de ações."""
        resultados = {}
        
        for acao in acoes:
            try:
                analise = agent.analyze_stock(
                    "Analise esta ação e dê uma recomendação", 
                    acao
                )
                resultados[acao] = analise
            except Exception as e:
                resultados[acao] = f"Erro: {e}"
        
        return resultados
    
    # Portfolio de exemplo
    portfolio = ["PETR4", "VALE3", "ITUB4"]
    
    print(f"📊 Analisando portfolio: {portfolio}")
    
    resultados = analisar_portfolio(portfolio)
    
    for acao, resultado in resultados.items():
        print(f"\n📈 {acao}:")
        print(f"   {resultado[:200]}..." if len(resultado) > 200 else f"   {resultado}")


if __name__ == "__main__":
    print("🚀 Exemplos de Uso do Agente Financeiro")
    print("=" * 50)
    
    # Executar exemplos
    exemplo_chat()
    exemplo_analise_acoes()
    exemplo_uso_programatico()
    
    print("\n✅ Exemplos concluídos!")
    print("\n💡 Dicas de uso:")
    print("   - Use agent.chat() para perguntas gerais")
    print("   - Use agent.analyze_stock() para análise de ações")
    print("   - O agente retorna strings formatadas em markdown") 