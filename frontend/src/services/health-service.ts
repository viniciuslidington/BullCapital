import type { HealthStatus } from "@/types/health";
import { api } from "./api";

export const HealthService = {
  check: async (): Promise<HealthStatus> => {
    const res = await api.get("/health");
    return res.data;
  },
};
