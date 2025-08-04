import { api } from "./api";

export const HealthService = {
  check: async () => {
    const res = await api.get("/health");
    return res.data;
  },
};
