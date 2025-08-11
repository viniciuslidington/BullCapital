export interface TickerInfo {
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

export interface MultiTickerResponse {
  symbols: string[];
  timestamp: string;
  results: TickerBasicInfoResponse;
}
export interface TickerBasicInfoResponse {
  timestamp: string;
  longName: string;
  sector: string;
  industry: string;
  employees: number;
  website: string;
  country: string;
  business_summary: string;
  fullExchangeName: string;
  type: string;
  currency: string;
  companyOfficers: {
    maxAge: number;
    name: string;
    age?: number | undefined; // nem todos têm
    title: string;
    yearBorn?: number | undefined; // nem todos têm
    fiscalYear: number;
    totalPay?: number | undefined; // nem todos têm
    exercisedValue: number;
    unexercisedValue: number;
  }[];
  logo: string | null;
  priceAndVariation: {
    currentPrice: number;
    previousClose: number;
    dayLow: number;
    dayHigh: number;
    fiftyTwoWeekLow: number;
    fiftyTwoWeekHigh: number;
    fiftyTwoWeekChangePercent: number;
    regularMarketChangePercent: number;
    regularMarketChange: number;
    regularMarketOpen: number;
    regularMarketDayRange: string;
    fiftyTwoWeekRange: string;
    fiftyDayAverage: number;
    twoHundredDayAverage: number;
  };
  volumeAndLiquidity: {
    volume: number;
    averageVolume10days: number;
    averageDailyVolume3Month: number;
    bid: number;
    ask: number;
  };
  riskAndMarketOpinion: {
    beta: number;
    recommendationKey: string;
    recommendationMean: number;
    targetHighPrice: number;
    targetLowPrice: number;
    targetMeanPrice: number;
    numberOfAnalystOpinions: number;
  };
  valuation: {
    marketCap: number;
    enterpriseValue: number;
    trailingPE: number;
    forwardPE: number;
    priceToBook: number;
    priceToSalesTrailing12Months: number;
    enterpriseToRevenue: number;
    enterpriseToEbitda: number;
  };
  rentability: {
    returnOnEquity: number;
    returnOnAssets: number;
    profitMargins: number;
    grossMargins: number;
    operatingMargins: number;
    ebitdaMargins: number;
  };
  eficiencyAndCashflow: {
    revenuePerShare: number;
    grossProfits: number;
    ebitda: number;
    operatingCashflow: number;
    freeCashflow: number;
    earningsQuarterlyGrowth: number;
    revenueGrowth: number;
    totalRevenue: number;
  };
  debtAndSolvency: {
    totalDebt: number;
    debtToEquity: number;
    quickRatio: number;
    currentRatio: number;
  };
  dividends: {
    dividendRate: number;
    dividendYield: number;
    payoutRatio: number;
    lastDividendValue: number;
    exDividendDate: string;
  };
  ShareholdingAndProfit: {
    sharesOutstanding: number;
    floatShares: number;
    heldPercentInsiders: number;
    heldPercentInstitutions: number;
    epsTrailingTwelveMonths: number;
    epsForward: number;
    netIncomeToCommon: number;
  };
}

export type CompanyOfficers = {
  maxAge: number;
  name: string;
  age?: number | undefined; // nem todos têm
  title: string;
  yearBorn?: number | undefined; // nem todos têm
  fiscalYear: number;
  totalPay?: number | undefined; // nem todos têm
  exercisedValue: number;
  unexercisedValue: number;
};
