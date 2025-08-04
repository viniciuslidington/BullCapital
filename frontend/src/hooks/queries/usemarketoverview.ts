import { useQuery } from "@tanstack/react-query";
import { MarketOverviewService } from "@/services/marketoverview-service";
import { getQueryConfig } from "./queries-config";

export function useMarketOverview(category: string) {
  return useQuery({
    queryKey: ["market-overview", category],
    queryFn: () => MarketOverviewService.getByCategory(category),
    ...getQueryConfig("marketData"), // Atualiza a cada 30s
  });
}
