import { useQuery } from "@tanstack/react-query";
import { DividendsService } from "@/services/dividends-service";

export function useDividends(symbol: string) {
  return useQuery({
    queryKey: ["dividends", symbol],
    queryFn: () => DividendsService.getDividends(symbol),
  });
}

export function useRecommendations(symbol: string) {
  return useQuery({
    queryKey: ["recommendations", symbol],
    queryFn: () => DividendsService.getRecommendations(symbol),
  });
}

export function useCalendar(symbol: string) {
  return useQuery({
    queryKey: ["calendar", symbol],
    queryFn: () => DividendsService.getCalendar(symbol),
  });
}
