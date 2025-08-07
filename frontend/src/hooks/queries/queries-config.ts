import { type QueryClientConfig } from "@tanstack/react-query";

// Intervalos de atualização automática
export const REFETCH_INTERVALS = {
  MARKET_DATA: 30_000, // 30 segundos
  PERFORMANCE: 120_000, // 3 minutos
  NEWS: 300_000, // 5 minutos
  HEALTH: 30_000, // 30 segundos
  PRICES: 15_000, // 15 segundos
  DIVIDENDS: 3_600_000, // 1 hora
  CALENDAR: 3_600_000, // 1 hora
} as const;

// Tempo que os dados permanecem "frescos"
export const STALE_TIME = {
  MARKET_DATA: 10_000, // 10 segundos
  STATIC_DATA: 3_600_000, // 1 hora
  SEARCH: 300_000, // 5 minutos
  HISTORY: 86_400_000, // 24 horas
  COMPANY_INFO: 86_400_000, // 24 horas
} as const;

// Tempo máximo de cache
export const CACHE_TIME = {
  MARKET_DATA: 300_000, // 5 minutos
  STATIC_DATA: 86_400_000, // 24 horas
  SEARCH: 600_000, // 10 minutos
  HISTORY: 604_800_000, // 7 dias
} as const;

// Configurações padrão para diferentes tipos de queries
export const QUERY_CONFIGS = {
  marketData: {
    refetchInterval: REFETCH_INTERVALS.MARKET_DATA,
    staleTime: STALE_TIME.MARKET_DATA,
    gcTime: CACHE_TIME.MARKET_DATA,
    retry: 2,
  },
  staticData: {
    refetchInterval: false,
    staleTime: STALE_TIME.STATIC_DATA,
    gcTime: CACHE_TIME.STATIC_DATA,
    retry: 1,
  },
  search: {
    refetchInterval: false,
    staleTime: STALE_TIME.SEARCH,
    gcTime: CACHE_TIME.SEARCH,
    retry: 0,
  },
  performance: {
    refetchInterval: REFETCH_INTERVALS.PERFORMANCE,
    staleTime: STALE_TIME.MARKET_DATA,
    gcTime: CACHE_TIME.MARKET_DATA,
    retry: 2,
  },
  news: {
    refetchInterval: REFETCH_INTERVALS.NEWS,
    staleTime: STALE_TIME.SEARCH,
    gcTime: CACHE_TIME.SEARCH,
    retry: 1,
  },
  dividends: {
    refetchInterval: REFETCH_INTERVALS.DIVIDENDS,
    staleTime: STALE_TIME.STATIC_DATA,
    gcTime: CACHE_TIME.STATIC_DATA,
    retry: 1,
  },
  calendar: {
    refetchInterval: REFETCH_INTERVALS.CALENDAR,
    staleTime: STALE_TIME.STATIC_DATA,
    gcTime: CACHE_TIME.STATIC_DATA,
    retry: 1,
  },
  health: {
    refetchInterval: REFETCH_INTERVALS.HEALTH,
    staleTime: 5000,
    gcTime: 10000,
    retry: 0,
  },
} as const;

// Configuração global do QueryClient
export const queryClientConfig: QueryClientConfig = {
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      refetchOnMount: true,
      refetchOnReconnect: true,
      retry: 1,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      staleTime: 0,
      gcTime: 300_000, // 5 minutos
    },
    mutations: {
      retry: 1,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
    },
  },
};

// Função para obter configuração baseada no tipo de query
export function getQueryConfig(type: keyof typeof QUERY_CONFIGS) {
  return QUERY_CONFIGS[type];
}
