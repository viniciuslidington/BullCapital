import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { HighlightsCard } from "./highlights-card";

// Mock de dados para a lista de "Altas"
const mockGainers = [
  { ticker: "AAPL", name: "Apple Inc.", price: 187.45, changePercent: 1.23 },
  {
    ticker: "MSFT",
    name: "Microsoft Corp.",
    price: 329.04,
    changePercent: 0.87,
  },
  { ticker: "NVDA", name: "NVIDIA Corp.", price: 485.09, changePercent: 1.78 },
  {
    ticker: "AMZN",
    name: "Amazon.com Inc.",
    price: 143.56,
    changePercent: 0.45,
  },
];

// Mock de dados para a lista de "Baixas"
const mockLosers = [
  { ticker: "TSLA", name: "Tesla Inc.", price: 211.32, changePercent: -2.14 },
  {
    ticker: "GOOGL",
    name: "Alphabet Inc.",
    price: 135.8,
    changePercent: -0.55,
  },
  {
    ticker: "META",
    name: "Meta Platforms",
    price: 310.45,
    changePercent: -1.02,
  },
  {
    ticker: "JNJ",
    name: "Johnson & Johnson",
    price: 160.15,
    changePercent: -0.21,
  },
];

export function HighlightsOverview() {
  return (
    <div className="flex w-full items-center gap-5">
      <Tabs defaultValue="account" className="w-full">
        <TabsList className="gap-2">
          <p className="text-muted-foreground dark:text-foreground mr-2 font-semibold">
            DESTAQUES
          </p>
          <TabsTrigger
            value="acoes"
            className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground cursor-pointer"
          >
            Ações
          </TabsTrigger>
          <TabsTrigger
            value="fiis"
            className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground cursor-pointer"
          >
            FIIs
          </TabsTrigger>
          <TabsTrigger
            value="etfs"
            className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground cursor-pointer"
          >
            ETFs
          </TabsTrigger>
          <TabsTrigger
            value="bdrs"
            className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground cursor-pointer"
          >
            BDRs
          </TabsTrigger>
        </TabsList>
        <TabsContent value="acoes" className="flex gap-5">
          <HighlightsCard title="Altas" items={mockGainers} />
          <HighlightsCard title="Baixas" items={mockLosers} />
          <HighlightsCard title="Mais Ativas" items={mockGainers} />
          <HighlightsCard title="Dividendos" items={mockGainers} />
        </TabsContent>
        <TabsContent value="fiis" className="flex gap-5">
          <HighlightsCard title="Altas" items={mockGainers} />
          <HighlightsCard title="Baixas" items={mockLosers} />
          <HighlightsCard title="Mais Ativas" items={mockGainers} />
          <HighlightsCard title="Dividendos" items={mockGainers} />
        </TabsContent>
        <TabsContent value="etfs" className="flex gap-5">
          <HighlightsCard title="Altas" items={mockGainers} />
          <HighlightsCard title="Baixas" items={mockLosers} />
          <HighlightsCard title="Mais Ativas" items={mockGainers} />
          <HighlightsCard title="Dividendos" items={mockGainers} />
        </TabsContent>
        <TabsContent value="bdrs" className="flex gap-5">
          <HighlightsCard title="Altas" items={mockGainers} />
          <HighlightsCard title="Baixas" items={mockLosers} />
          <HighlightsCard title="Mais Ativas" items={mockGainers} />
          <HighlightsCard title="Dividendos" items={mockGainers} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
