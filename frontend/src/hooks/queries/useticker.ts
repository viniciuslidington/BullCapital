import { useQuery } from "@tanstack/react-query";
import { TickersService } from "@/services/tickers-service";
import { getQueryConfig } from "./queries-config";

export function useMultiTickers(symbols: string) {
  return useQuery({
    queryKey: ["tickers-multi", symbols],
    queryFn: () => TickersService.getMultiInfo(symbols),
    ...getQueryConfig("marketData"), // Atualiza a cada 30s
  });
}

export function useTickerInfo(symbol: string) {
  return useQuery({
    queryKey: ["ticker-info", symbol],
    queryFn: () => TickersService.getBasicInfo(symbol),
    ...getQueryConfig("marketData"), // Atualiza a cada 30s
  });
}

export function useTickerFullData(symbol: string) {
  return useQuery({
    queryKey: ["ticker-full", symbol],
    queryFn: () => TickersService.getFullData(symbol),
    ...getQueryConfig("marketData"), // Atualiza a cada 30s
  });
}
