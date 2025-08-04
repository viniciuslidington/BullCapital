import { useQuery } from "@tanstack/react-query";
import { CategoriesService } from "@/services/categories-service";
import type { Categorias, Setores } from "@/types/category";
import { getQueryConfig } from "./queries-config";

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: () => CategoriesService.listAll(),
    ...getQueryConfig("marketData"),
  });
}

export function useCategoryScreening(
  categoria: Categorias,
  options?: {
    setor?: Setores;
    limit?: number;
    offset?: number;
    sort_field?: string;
    sort_asc?: boolean;
  },
) {
  return useQuery({
    queryKey: ["category-screening", categoria, options],
    queryFn: () => CategoriesService.getByCategory(categoria, options),
  });
}
