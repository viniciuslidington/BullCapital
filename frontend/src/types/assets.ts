export interface StockItem {
  ticker: string;
  nome: string;
  preco: number;
  changePercent: number;
  currency: string;
}

export interface DividendItem {
  ticker: string;
  nome: string;
  dividendo: number;
  currency: string;
  dy: number;
  tipo: string;
  dataCom: string;
  dataEx: string;
  dataPagamento: string;
}

export type CategoriasType = "acoes" | "fiis" | "etfs" | "bdrs";

export type IndexesType =
  | "price"
  | "priceChangePercent"
  | "roe"
  | "dy"
  | "yearHigh"
  | "marketCap"
  | "peRatio"
  | "netMargin"
  | "pFfo"
  | "pVp";
