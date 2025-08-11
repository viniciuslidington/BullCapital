import { useState, useCallback } from 'react';
import { AIService } from '@/services/ai-service';
import type { ChatMessage } from '@/types/ai';

export function useAIChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const addMessage = useCallback((content: string, type: 'user' | 'ai') => {
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      content,
      type,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage;
  }, []);

  const sendMessage = useCallback(async (userMessage: string) => {
    if (!userMessage.trim()) return;

    setError(null);
    setIsLoading(true);

    // Adicionar mensagem do usuário
    addMessage(userMessage, 'user');

    try {
      // Enviar para o AI Service com conversation_id (se existir)
      const response = await AIService.chat(userMessage, conversationId || undefined);
      // Salvar conversation_id retornado (para manter contexto)
      if (response.conversation_id) setConversationId(response.conversation_id);
      
      // Adicionar resposta da IA
      addMessage(response.content, 'ai');
    } catch (err) {
      console.error('Erro ao enviar mensagem:', err);
      setError('Erro ao enviar mensagem. Tente novamente.');
      
      // Adicionar mensagem de erro
      addMessage('Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.', 'ai');
    } finally {
      setIsLoading(false);
    }
  }, [addMessage, conversationId]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
    setConversationId(null);
  }, []);

  // Função para analisar ticker específico
  const analyzeStock = useCallback(async (ticker: string, question?: string) => {
    const query = question || `Faça uma análise completa da ${ticker}`;
    await sendMessage(query);
  }, [sendMessage]);

  // Função para obter dados financeiros específicos
  const getFinanceData = useCallback(async (ticker: string) => {
    setIsLoading(true);
    try {
      const data = await AIService.getFinanceData(ticker);
      
      // Formatar dados para exibição
      const formattedMessage = `
📊 **Análise Financeira - ${data.ticker}**

**Valuation (Preço Justo):**
${Object.entries(data.valuation.metodos).map(([method, info]) => 
  `• ${info.comentario}: ${info.preco_justo ? `R$ ${info.preco_justo.toFixed(2)}` : 'N/A'}`
).join('\n')}

**Múltiplos:**
• P/L: ${data.multiplos.pl || 'N/A'}
• P/VP: ${data.multiplos.pvp || 'N/A'}
• EV/EBITDA: ${data.multiplos.ev_ebitda || 'N/A'}
• EV/Receita: ${data.multiplos.ev_receita || 'N/A'}

**Preço Justo Médio:** ${data.valuation.media_precos ? `R$ ${data.valuation.media_precos.toFixed(2)}` : 'N/A'}
      `;

      addMessage(`Analisar ${ticker}`, 'user');
      addMessage(formattedMessage, 'ai');
    } catch (err) {
      console.error('Erro ao obter dados financeiros:', err);
      addMessage(`Analisar ${ticker}`, 'user');
      addMessage('Erro ao obter dados financeiros. Tente novamente.', 'ai');
    } finally {
      setIsLoading(false);
    }
  }, [addMessage]);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    analyzeStock,
    getFinanceData,
    conversationId,
  };
} 