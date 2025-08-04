import { api } from "./api";

export const MarketOverviewService = {
  getByCategory: async (category: string) => {
    const res = await api.get(`/market-overview/${category}`);
    return res.data;
  },
};
