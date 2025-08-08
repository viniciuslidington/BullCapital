import { useQuery } from "@tanstack/react-query";
import { HealthService } from "@/services/health-service";
import { getQueryConfig } from "./queries-config";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => HealthService.check(),
    ...getQueryConfig("health"), // Atualiza a cada 30s
  });
}
