export interface SearchResult {
  symbol: string;
  name: string;
  exchange: string;
  type: string;
  score: number;
  sector: string;
  industry: string;
  logo: string | null;
}

export interface SearchResponse {
  query: string;
  count: number;
  results: SearchResult[];
}

export interface LookupResponse {
  query: string;
  type: string;
  results: Array<{
    symbol: string;
    name: string;
    type: string;
    exchange: string;
    country: string;
    currency: string;
  }>;
}
