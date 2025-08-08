"""
Pacote Agent - Agente Financeiro para Análise Fundamentalista.

Este pacote contém:
- financial_agent.py: Agente principal com lógica de análise
- api_server.py: Servidor HTTP para expor o agente como API
- test_api.py: Testes da API e do agente
- example_agent.py: Exemplos de uso direto
"""

from .financial_agent import agent, FinancialAgent

__all__ = ['agent', 'FinancialAgent']
__version__ = '1.0.0' 