export interface ChatMessage {
  id: string;
  content: string;
  type: 'user' | 'ai';
  timestamp: Date;
}

export interface ChatRequest {
  question: string;
}

export interface ChatResponse {
  content: string;
  conversation_id: string;
}

export interface FinanceData {
  ticker: string;
  valuation: {
    metodos: {
      [key: string]: {
        preco_justo: number | null;
        comentario: string;
      };
    };
    media_precos: number | null;
  };
  multiplos: {
    pl: number | null;
    pvp: number | null;
    ev_ebitda: number | null;
    ev_receita: number | null;
  };
}

export interface ValuationResponse {
  markdown: string;
}

export interface MultiplesResponse {
  markdown: string;
}

export interface CampResponse {
  ticker: string;
  ke_pct: number | null;
  dividend_ttm: number | null;
  g_dividendo: number;
  camp_price: number | null;
} 