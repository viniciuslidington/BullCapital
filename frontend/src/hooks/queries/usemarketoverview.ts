import { useQuery } from "@tanstack/react-query";
import { MarketOverviewService } from "@/services/marketoverview-service";

export function useMarketOverview(category: string) {
  return useQuery({
    queryKey: ["market-overview", category],
    queryFn: () => MarketOverviewService.getByCategory(category),
    refetchInterval: 30000, // Auto refresh every 30 seconds
  });
}
