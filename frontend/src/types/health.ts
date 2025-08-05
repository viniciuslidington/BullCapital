export interface HealthStatus {
  status: "healthy" | "unhealthy";
  service: string;
  timestamp: string;
  test_ticker: string;
  test_successful: boolean;
}
