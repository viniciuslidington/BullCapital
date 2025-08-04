import type { HistoryResponse, Interval, Period } from "@/types/history";
import { api } from "./api";

export const HistoryService = {
  getBySymbol: async (
    symbol: string,
    period?: Period,
    interval?: Interval,
  ): Promise<HistoryResponse> => {
    const res = await api.get(`/${symbol}/history`, {
      params: { symbol, period, interval },
    });
    return res.data;
  },

  getMulti: async (
    symbols: string,
    period?: Period,
    interval?: Interval,
  ): Promise<HistoryResponse> => {
    const res = await api.get("/multi-history", {
      params: { symbols, period, interval },
    });
    return res.data;
  },
};
