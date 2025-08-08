import type { LookupResponse, SearchResponse } from "@/types/search";
import { api } from "./api";

export const SearchService = {
  search: async (query: string, limit = 10): Promise<SearchResponse> => {
    const res = await api.get("/search", {
      params: { query: query, limit },
    });
    return res.data;
  },

  lookup: async (
    query: string,
    type: string = "all",
    count = 25,
  ): Promise<LookupResponse> => {
    const res = await api.get("/lookup", {
      params: { query, type, count },
    });
    return res.data;
  },
};
