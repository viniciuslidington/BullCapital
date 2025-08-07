import type { MarketOverviewResponse } from "@/types/marketoverview";
import { api } from "./api";

export const MarketOverviewService = {
  getByCategory: async (category: string): Promise<MarketOverviewResponse> => {
    const res = await api.get(`/market-overview/${category}`);
    return res.data;
  },
};
