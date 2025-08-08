export interface DividendInfo {
  symbol: string;
  dividends: Array<{
    date: string;
    dividend: number;
  }>;
}

export interface RecommendationInfo {
  symbol: string;
  recommendations: Array<{
    date: string;
    firm: string;
    toGrade: string;
    fromGrade: string;
    action: string;
  }>;
}

export interface CalendarInfo {
  symbol: string;
  calendar: {
    earnings: Array<{
      date: string;
      epsEstimate: number;
      epsActual: number;
      revenue: number;
    }>;
    dividends: Array<{
      date: string;
      dividend: number;
      type: string;
    }>;
  };
}
