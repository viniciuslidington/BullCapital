import { useQuery } from "@tanstack/react-query";
import { TickersService } from "@/services/tickers-service";

export function useMultiTickers(symbols: string) {
  return useQuery({
    queryKey: ["tickers-multi", symbols],
    queryFn: () => TickersService.getMultiInfo(symbols),
  });
}

export function useTickerInfo(symbol: string) {
  return useQuery({
    queryKey: ["ticker-info", symbol],
    queryFn: () => TickersService.getBasicInfo(symbol),
  });
}

export function useTickerFullData(symbol: string) {
  return useQuery({
    queryKey: ["ticker-full", symbol],
    queryFn: () => TickersService.getFullData(symbol),
  });
}
