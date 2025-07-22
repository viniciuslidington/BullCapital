import { AssetChart } from "@/components/features/assets-chart/asset-chart";
import { HighlightsOverview } from "@/components/features/highlights-overview/highlights-overview";
import { MarketOverview } from "@/components/features/market-overview/market-overview";
import { ChartTabs } from "@/components/features/markets-chart/chart-tabs";
import { SearchBar } from "@/components/ui/search-bar";

export function Home() {
  return (
    <div className="flex h-auto w-full max-w-[1180px] flex-col gap-8 p-8">
      <MarketOverview />
      <SearchBar />
      <HighlightsOverview />
      <ChartTabs />
      <AssetChart />
    </div>
  );
}
