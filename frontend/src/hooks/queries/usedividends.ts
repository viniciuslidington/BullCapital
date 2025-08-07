import { useQuery } from "@tanstack/react-query";
import { DividendsService } from "@/services/dividends-service";
import { getQueryConfig } from "./queries-config";

export function useDividends(symbol: string) {
  return useQuery({
    queryKey: ["dividends", symbol],
    queryFn: () => DividendsService.getDividends(symbol),
    ...getQueryConfig("dividends"), // Atualiza a cada 1h
  });
}

export function useRecommendations(symbol: string) {
  return useQuery({
    queryKey: ["recommendations", symbol],
    queryFn: () => DividendsService.getRecommendations(symbol),
    ...getQueryConfig("dividends"), // Atualiza a cada 1h
  });
}

export function useCalendar(symbol: string) {
  return useQuery({
    queryKey: ["calendar", symbol],
    queryFn: () => DividendsService.getCalendar(symbol),
    ...getQueryConfig("dividends"), // Atualiza a cada 1h
  });
}
