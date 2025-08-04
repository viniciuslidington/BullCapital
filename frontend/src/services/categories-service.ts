import { api } from "./api";

export const CategoriesService = {
  listAll: async () => {
    const res = await api.get("/categorias");
    return res.data;
  },

  getByCategory: async (
    categoria: string,
    options?: {
      setor?: string;
      limit?: number;
      offset?: number;
      sort_field?: string;
      sort_asc?: boolean;
    },
  ) => {
    const res = await api.get(`/categorias/${categoria}`, {
      params: {
        ...options,
      },
    });
    return res.data;
  },
};
