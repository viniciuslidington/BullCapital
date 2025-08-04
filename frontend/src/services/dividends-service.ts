import { api } from "./api";

export const DividendsService = {
  getDividends: async (symbol: string) => {
    const res = await api.get(`/${symbol}/dividends`);
    return res.data;
  },

  getRecommendations: async (symbol: string) => {
    const res = await api.get(`/${symbol}/recommendations`);
    return res.data;
  },

  getCalendar: async (symbol: string) => {
    const res = await api.get(`/${symbol}/calendar`);
    return res.data;
  },
};
