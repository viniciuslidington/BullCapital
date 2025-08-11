import axios from "axios";
import type { 
  ChatRequest, 
  ChatResponse, 
  FinanceData, 
  ValuationResponse, 
  MultiplesResponse, 
  CampResponse 
} from "@/types/ai";

const AI_BASE_URL = "http://localhost:8001";

// Instância com timeout e retry simples
const http = axios.create({
  baseURL: AI_BASE_URL,
  timeout: 20000, // 20s
});

async function withRetry<T>(fn: () => Promise<T>, retries = 1): Promise<T> {
  try {
    return await fn();
  } catch (e) {
    if (retries <= 0) throw e;
    return await withRetry(fn, retries - 1);
  }
}

export const AIService = {
  chat: async (question: string, conversationId?: string): Promise<ChatResponse> => {
    const payload: ChatRequest & { conversation_id?: string } = { question };
    if (conversationId) payload.conversation_id = conversationId;
    return withRetry(async () => {
      const response = await http.post(`/chat`, payload);
      return response.data;
    });
  },

  getFinanceData: async (ticker: string): Promise<FinanceData> => {
    return withRetry(async () => {
      const response = await http.get(`/finance/${ticker}`);
      return response.data;
    });
  },

  getValuation: async (ticker: string): Promise<ValuationResponse> => {
    return withRetry(async () => {
      const response = await http.get(`/valuation/${ticker}`);
      return response.data;
    });
  },

  getMultiples: async (ticker: string): Promise<MultiplesResponse> => {
    return withRetry(async () => {
      const response = await http.get(`/multiples/${ticker}`);
      return response.data;
    });
  },

  getCapm: async (ticker: string): Promise<CampResponse> => {
    return withRetry(async () => {
      const response = await http.get(`/capm/${ticker}`);
      return response.data;
    });
  },

  getNews: async (query: string): Promise<{ markdown: string }> => {
    return withRetry(async () => {
      const response = await http.get(`/news`, { params: { q: query } });
      return response.data;
    });
  },

  health: async (): Promise<{ ok: boolean; service: string }> => {
    const response = await http.get(`/health`);
    return response.data;
  }
}; 