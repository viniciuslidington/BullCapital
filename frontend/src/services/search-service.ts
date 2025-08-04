import { api } from "./api";

export const SearchService = {
  search: async (query: string, limit = 10) => {
    const res = await api.get("/search", {
      params: { q: query, limit },
    });
    return res.data;
  },

  lookup: async (query: string, type: string = "all", count = 25) => {
    const res = await api.get("/lookup", {
      params: { query, type, count },
    });
    return res.data;
  },
};
