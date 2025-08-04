import { api } from "./api";

export const PerformanceService = {
  getPeriodPerformance: async (symbols: string) => {
    const res = await api.get("/period-performance", {
      params: { symbols },
    });
    return res.data;
  },
};
