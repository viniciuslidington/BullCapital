import { useQuery } from "@tanstack/react-query";
import { HistoryService } from "@/services/history-service";
import type { Period, Interval } from "@/types/history";

export function useHistory(
  symbol: string,
  period?: Period,
  interval?: Interval,
) {
  return useQuery({
    queryKey: ["history", symbol, period, interval],
    queryFn: () => HistoryService.getBySymbol(symbol, period, interval),
  });
}

export function useMultiHistory(
  symbols: string,
  period?: Period,
  interval?: Interval,
) {
  return useQuery({
    queryKey: ["multi-history", symbols, period, interval],
    queryFn: () => HistoryService.getMulti(symbols, period, interval),
  });
}
