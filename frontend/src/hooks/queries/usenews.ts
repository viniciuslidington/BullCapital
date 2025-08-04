import { useQuery } from "@tanstack/react-query";
import { NewsService } from "@/services/news-service";

export function useNews(symbol: string, num: number = 5) {
  return useQuery({
    queryKey: ["news", symbol, num],
    queryFn: () => NewsService.getNews(symbol, num),
    refetchInterval: 300000, // Refresh every 5 minutes
  });
}
