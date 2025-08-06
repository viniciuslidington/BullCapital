import { AssetChart } from "@/components/features/assets-chart/asset-chart";
import { HighlightsOverview } from "@/components/features/highlights-overview/highlights-overview";
import { MarketOverview } from "@/components/features/market-overview/market-overview";
import { ChartTabs } from "@/components/features/markets-chart/chart-tabs";
import { Button } from "@/components/ui/button";
import { SearchBar } from "@/components/ui/search-bar";
import { ChartNoAxesCombined } from "lucide-react";

export function Home() {
  return (
    <div className="flex h-auto w-full max-w-[1180px] flex-col gap-8 p-8">
      <MarketOverview />
      <div className="flex flex-col items-center gap-12 pt-10 pb-16">
        <h1 className="text-gradient bg-gradient-to-tr from-indigo-400 via-purple-500 to-indigo-600 text-center text-4xl font-semibold dark:from-slate-600 dark:via-slate-400 dark:to-slate-50">
          Eleve seu nível como os grandes investidores <br /> e tome decisões
          com confiança
        </h1>
        <SearchBar />
        <Button
          variant="outline"
          className="cursor-pointer rounded-3xl text-xs"
        >
          <ChartNoAxesCombined></ChartNoAxesCombined>
          Ver Ranking de ativos
        </Button>
      </div>
      <HighlightsOverview />
      <ChartTabs />
      <AssetChart />
    </div>
  );
}
