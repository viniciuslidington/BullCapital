import type { PeriodPerformanceResponse } from "@/types/performance";
import { api } from "./api";

export const PerformanceService = {
  getPeriodPerformance: async (
    symbols: string,
  ): Promise<PeriodPerformanceResponse> => {
    const res = await api.get("/period-performance", {
      params: { symbols },
    });
    return res.data;
  },
};
