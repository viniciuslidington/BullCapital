import { api } from "./api";

export const HistoryService = {
  getBySymbol: async (symbol: string, period?: string, interval?: string) => {
    const res = await api.get(`/${symbol}/history`, {
      params: { symbol, period, interval },
    });
    return res.data;
  },

  getMulti: async (symbols: string, period?: string, interval?: string) => {
    const res = await api.get("/multi-history", {
      params: { symbols, period, interval },
    });
    return res.data;
  },
};
