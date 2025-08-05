import { useQuery } from "@tanstack/react-query";
import { PerformanceService } from "@/services/performance-service";
import { getQueryConfig } from "./queries-config";

export function usePerformance(symbols: string) {
  return useQuery({
    queryKey: ["performance", symbols],
    queryFn: () => PerformanceService.getPeriodPerformance(symbols),
    ...getQueryConfig("performance"), // Atualiza a cada 3min
  });
}
