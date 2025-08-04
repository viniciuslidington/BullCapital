import { useQuery } from "@tanstack/react-query";
import { HealthService } from "@/services/health-service";

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => HealthService.check(),
    refetchInterval: 30000, // Check health every 30 seconds
  });
}
