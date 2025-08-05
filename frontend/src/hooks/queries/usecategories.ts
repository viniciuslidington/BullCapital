import { useQueries, useQuery } from "@tanstack/react-query";
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

const CATEGORIAS: {
  nome: Categorias;
  options: {
    limit: number;
    sort_field: string;
    sort_asc: boolean;
  };
}[] = [
  {
    nome: "alta_do_dia",
    options: { limit: 5, sort_field: "percentchange", sort_asc: false },
  },
  {
    nome: "baixa_do_dia",
    options: { limit: 5, sort_field: "percentchange", sort_asc: true },
  },
  {
    nome: "mais_negociadas",
    options: { limit: 5, sort_field: "dayvolume", sort_asc: false },
  },
  {
    nome: "valor_dividendos",
    options: {
      limit: 5,
      sort_field: "forward_dividend_yield",
      sort_asc: false,
    },
  },
];

// Hook para múltiplas categorias com setor opcional
export function useMultipleCategoryScreenings(setor?: Setores) {
  const queries = useQueries({
    queries: CATEGORIAS.map(({ nome, options }) => ({
      queryKey: ["category-screening", nome, { ...options, setor }],
      queryFn: () =>
        CategoriesService.getByCategory(nome, {
          ...options,
          setor,
        }),
      ...getQueryConfig("marketData"),
    })),
  });

  const isLoading = queries.some((r) => r.isLoading);
  const isFetching = queries.some((r) => r.isFetching);
  const isError = queries.some((r) => r.isError);
  const data = Object.fromEntries(
    CATEGORIAS.map((c, i) => [c.nome, queries[i].data?.resultados || []]),
  );

  return { isLoading, isError, data, isFetching };
}
