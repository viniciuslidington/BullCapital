import type {
  MultiTickerResponse,
  TickerBasicInfoResponse,
} from "@/types/ticker";
import { api } from "./api";

export const TickersService = {
  getMultiInfo: async (symbols: string): Promise<MultiTickerResponse> => {
    const res = await api.get("/multi-info", { params: { symbols } });
    return res.data;
  },

  getBasicInfo: async (symbol: string): Promise<TickerBasicInfoResponse> => {
    const res = await api.get(`/${symbol}/info`);
    return res.data;
  },

  getFullData: async (symbol: string) => {
    const res = await api.get(`/${symbol}/fulldata`);
    return res.data;
  },
};
