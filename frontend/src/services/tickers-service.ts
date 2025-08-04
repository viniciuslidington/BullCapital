import { api } from "./api";

export const TickersService = {
  getMultiInfo: async (symbols: string) => {
    const res = await api.get("/multi-info", { params: { symbols } });
    return res.data;
  },

  getBasicInfo: async (symbol: string) => {
    const res = await api.get(`/${symbol}/info`);
    return res.data;
  },

  getFullData: async (symbol: string) => {
    const res = await api.get(`/${symbol}/fulldata`);
    return res.data;
  },
};
