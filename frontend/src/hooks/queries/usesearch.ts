import { useQuery } from "@tanstack/react-query";
import { SearchService } from "@/services/search-service";

export function useSearch(query: string, limit: number = 10) {
  return useQuery({
    queryKey: ["search", query, limit],
    queryFn: () => SearchService.search(query, limit),
    enabled: query.length > 0, // Only run if query exists
  });
}

export function useLookup(
  query: string,
  type: string = "all",
  count: number = 25,
) {
  return useQuery({
    queryKey: ["lookup", query, type, count],
    queryFn: () => SearchService.lookup(query, type, count),
    enabled: query.length > 0,
  });
}
