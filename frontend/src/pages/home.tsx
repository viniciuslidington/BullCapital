import { AssetChart } from "@/components/features/assets-chart/asset-chart";
import { HighlightsOverview } from "@/components/features/highlights-overview/highlights-overview";
import { MarketOverview } from "@/components/features/market-overview/market-overview";
import { ChartTabs } from "@/components/features/markets-chart/chart-tabs";
import { Button } from "@/components/ui/button";
import { SearchBar } from "@/components/ui/search-bar";
import { ChartNoAxesCombined } from "lucide-react";
import { useNavigate } from "react-router-dom";

export function Home() {
  return (
    <div className="flex h-auto w-full max-w-[1180px] flex-col gap-12 p-8 pb-16">
      <MarketOverview />
      <div className="flex flex-col items-center gap-12 pt-10 pb-16">
        <h1 className="text-gradient bg-gradient-to-tr from-indigo-300 via-purple-500 to-indigo-600 text-center text-4xl font-semibold dark:from-slate-600 dark:via-slate-400 dark:to-slate-50">
          Eleve seu nível como os grandes investidores <br /> e tome decisões
          com confiança
        </h1>
        <SearchBar />
        <NavSearch />
      </div>
      <HighlightsOverview />
      <ChartTabs />
      <AssetChart />
    </div>
  );
}

function NavSearch() {
  const navigate = useNavigate();
  return (
    <nav className="flex items-center gap-4">
      <Button
        variant="outline"
        className="bg-card/60 cursor-pointer rounded-3xl text-xs"
        onClick={() => navigate("/ranking")}
      >
        <ChartNoAxesCombined></ChartNoAxesCombined>
        Ver Ranking de ativos
      </Button>
      <span className="border-border h-full border-r"></span>

      <span className="flex items-center gap-2">
        <p className="text-sm">Mais Buscados:</p>
        <Button
          variant="outline"
          size="sm"
          className="bg-card/60 cursor-pointer rounded-3xl text-xs"
          onClick={() => navigate("ITSA4.SA")}
        >
          Itausa
        </Button>
        <Button
          variant="outline"
          className="bg-card/60 cursor-pointer rounded-3xl text-xs"
          size="sm"
          onClick={() => navigate("TAEE11.SA")}
        >
          Teasa
        </Button>
        <Button
          variant="outline"
          className="bg-card/60 cursor-pointer rounded-3xl text-xs"
          size="sm"
          onClick={() => navigate("TSLA")}
        >
          Tesla
        </Button>
        <Button
          variant="outline"
          className="bg-card/60 cursor-pointer rounded-3xl text-xs"
          size="sm"
          onClick={() => navigate("AAPL")}
        >
          Apple
        </Button>
      </span>
    </nav>
  );
}
