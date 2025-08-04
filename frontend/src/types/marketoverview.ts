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
  category: string;
  timestamp: string;
  count: number;
  data: MarketOverviewItem[];
}
