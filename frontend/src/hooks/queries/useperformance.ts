import { useQuery } from "@tanstack/react-query";
import { PerformanceService } from "@/services/performance-service";

export function usePerformance(symbols: string) {
  return useQuery({
    queryKey: ["performance", symbols],
    queryFn: () => PerformanceService.getPeriodPerformance(symbols),
    refetchInterval: 60000, // Refresh every minute
  });
}
