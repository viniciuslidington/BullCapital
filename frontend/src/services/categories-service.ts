import type {
  CategoriaResponse,
  Categorias,
  CategoriaScreeningResponse,
  Setores,
} from "@/types/category";
import { api } from "./api";

type SortField =
  | "intradaymarketcap"
  | "percentchange"
  | "dayvolume"
  | "forward_dividend_yield"
  | "avgdailyvol3m"
  | "beta"
  | string;

export const CategoriesService = {
  listAll: async (): Promise<CategoriaResponse> => {
    const res = await api.get("/categorias");
    return res.data;
  },

  getByCategory: async (
    categoria: Categorias,
    options?: {
      setor?: Setores;
      limit?: number;
      offset?: number;
      sort_field?: SortField;
      sort_asc?: boolean;
    },
  ): Promise<CategoriaScreeningResponse> => {
    const res = await api.get(`/categorias/${categoria}`, {
      params: {
        ...options,
      },
    });
    return res.data;
  },
};
