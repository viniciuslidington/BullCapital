export type Categorias =
  | "alta_do_dia"
  | "baixa_do_dia"
  | "mais_negociadas"
  | "small_caps_crescimento"
  | "valor_dividendos"
  | "baixo_pe"
  | "alta_liquidez"
  | "crescimento_lucros"
  | "baixo_risco"
  | "mercado_br"
  | "mercado_todo";

export type Setores =
  | "Basic Materials"
  | "Communication Services"
  | "Consumer Cyclical"
  | "Consumer Defensive"
  | "Energy"
  | "Financial Services"
  | "Healthcare"
  | "Industrials"
  | "Real Estate"
  | "Technology"
  | "Utilities";

export interface CategoriaResponse {
  categorias: Categorias[];
  descricoes: {
    [K in Categorias]?: string;
  };
}

export interface CategoriaResult {
  symbol: string;
  name: string;
  sector: string;
  price: number;
  change: number;
  volume: number;
  market_cap: number;
  pe_ratio: number;
  dividend_yield: number;
  fiftyTwoWeekChangePercent: number;
  avg_volume_3m: number;
  returnOnEquity: number;
  book_value: number;
  exchange: string;
  fullExchangeName: string;
  currency: string;
  website: string;
  logo: string | null;
}

export interface CategoriaScreeningResponse {
  categoria: Categorias;
  resultados: CategoriaResult[];
  total: number;
  total_disponivel: number;
  offset: number;
  limit: number;
  ordenacao: {
    campo: string;
    ascendente: boolean;
  };
}
