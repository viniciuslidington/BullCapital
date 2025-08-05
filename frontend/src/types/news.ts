export interface NewsItem {
  id: string;
  title: string;
  date: string;
  summary: string;
  url?: string;
  thumbnail?: string;
}

export interface NewsResponse {
  symbol: string;
  news: NewsItem[];
}
