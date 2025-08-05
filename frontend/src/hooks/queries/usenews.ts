import { useQuery } from "@tanstack/react-query";
import { NewsService } from "@/services/news-service";
import { getQueryConfig } from "./queries-config";

export function useNews(symbol: string, num: number = 5) {
  return useQuery({
    queryKey: ["news", symbol, num],
    queryFn: () => NewsService.getNews(symbol, num),
    ...getQueryConfig("news"), // Atualiza a cada 5min
  });
}
