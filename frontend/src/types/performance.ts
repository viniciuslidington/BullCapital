export interface PeriodData {
  change_percent: number;
  start_price: number;
  end_price: number;
  start_date: string;
  end_date: string;
}

export interface TickerPerformance {
  name: string;
  current_price: number;
  currency: string;
  logo?: string;
  performance: {
    [period: string]: PeriodData | null;
  };
}

export interface PeriodPerformanceResponse {
  timestamp: string;
  symbols_count: number;
  results: Record<string, {
    success: boolean;
    data: TickerPerformance | null;
    error?: string;
  }>;
}
