import { useQuery } from "@tanstack/react-query";
import { HistoryService } from "@/services/history-service";
import type { Period, Interval } from "@/types/history";
import { getQueryConfig } from "./queries-config";

// Função auxiliar para determinar o intervalo de atualização
function getRefetchInterval(interval?: Interval): number {
  switch (interval) {
    case "1m":
      return 60_000; // 1 minuto
    case "2m":
      return 120_000; // 2 minutos
    case "5m":
      return 300_000; // 5 minutos
    case "15m":
      return 900_000; // 15 minutos
    case "30m":
      return 1_800_000; // 30 minutos
    case "60m":
    case "1h":
      return 3_600_000; // 1 hora
    case "1d":
      return 86_400_000; // 1 dia
    default:
      return 0; // Sem atualização automática
  }
}

export function useHistory(
  symbol: string,
  period?: Period,
  interval?: Interval,
) {
  const config = {
    ...getQueryConfig("staticData"),
    refetchInterval: getRefetchInterval(interval),
  };

  return useQuery({
    queryKey: ["history", symbol, period, interval],
    queryFn: () => HistoryService.getBySymbol(symbol, period, interval),
    ...config,
  });
}

export function useMultiHistory(
  symbols: string,
  period?: Period,
  interval?: Interval,
) {
  const config = {
    ...getQueryConfig("staticData"),
    refetchInterval: getRefetchInterval(interval),
  };

  return useQuery({
    queryKey: ["multi-history", symbols, period, interval],
    queryFn: () => HistoryService.getMulti(symbols, period, interval),
    ...config,
  });
}
