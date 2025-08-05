import type { NewsResponse } from "@/types/news";
import { api } from "./api";

export const NewsService = {
  getNews: async (symbol: string, num = 5): Promise<NewsResponse> => {
    const res = await api.get(`/${symbol}/news`, { params: { num } });
    return res.data;
  },
};
