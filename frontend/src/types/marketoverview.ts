export interface MarketOverviewItem {
  symbol: string;
  name: string;
  price: number;
  change: number;
  website?: string;
  currency?: string;
  logo?: string;
}

export interface MarketOverviewResponse {
  category: "all" | "brasil" | "eua" | "europa" | "asia" | "moedas";
  timestamp: string;
  count: number;
  data: MarketOverviewItem[];
}
