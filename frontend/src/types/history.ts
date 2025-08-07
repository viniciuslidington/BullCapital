export type Period =
  | "1d"
  | "5d"
  | "1mo"
  | "3mo"
  | "6mo"
  | "1y"
  | "2y"
  | "5y"
  | "10y"
  | "ytd"
  | "max";
export type Interval =
  | "1m"
  | "2m"
  | "5m"
  | "15m"
  | "30m"
  | "60m"
  | "90m"
  | "1h"
  | "1d"
  | "5d"
  | "1wk"
  | "1mo"
  | "3mo";

export interface HistoryEntry {
  Date: string;
  Open: number;
  High: number;
  Low: number;
  Close: number;
  Volume: number;
  Dividends?: number;
  StockSplits?: number;
}

export interface HistoryResponse {
  symbol: string;
  period: string;
  interval: string;
  data: HistoryEntry[];
}
