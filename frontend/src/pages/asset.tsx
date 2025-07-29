import { MarketChart } from "@/components/features/markets-chart/market-chart";
import { PathLink } from "@/components/ui/path-link";
import {
  formatChange,
  formatDate,
  formatNumber,
  formatPrice,
} from "@/lib/utils";
import { ArrowDown, ArrowUp, Dot } from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TabsContent } from "@radix-ui/react-tabs";

const response = {
  symbol: "AAPL",
  company_name: "Apple Inc.",
  current_price: 214.41,
  previous_close: 214.15,
  change: 0.26,
  change_percent: 0.12,
  volume: 13295981,
  avg_volume: 53119755,
  currency: "USD",
  timezone: null,
  last_updated: "2025-07-24T14:49:18.804774",
  fundamentals: {
    market_cap: 3202235498496,
    pe_ratio: 33.395638,
    dividend_yield: 0.49,
    eps: 6.42,
    book_value: 4.471,
    debt_to_equity: 146.994,
    roe: 1.38015,
    roa: 0.23809999,
    sector: "Technology",
    industry: "Consumer Electronics",
    fifty_two_week_high: 260.1,
    fifty_two_week_low: 169.21,
  },
  historical_data: [
    {
      date: "2025-06-24",
      open: 202.59,
      high: 203.44,
      low: 200.2,
      close: 200.3,
      volume: 54064000,
      adj_close: 200.3,
    },
    {
      date: "2025-06-25",
      open: 201.45,
      high: 203.67,
      low: 200.62,
      close: 201.56,
      volume: 39525700,
      adj_close: 201.56,
    },
    {
      date: "2025-06-26",
      open: 201.43,
      high: 202.64,
      low: 199.46,
      close: 201,
      volume: 50799100,
      adj_close: 201,
    },
    {
      date: "2025-06-27",
      open: 201.89,
      high: 203.22,
      low: 200,
      close: 201.08,
      volume: 73188600,
      adj_close: 201.08,
    },
    {
      date: "2025-06-30",
      open: 202.01,
      high: 207.39,
      low: 199.26,
      close: 205.17,
      volume: 91912800,
      adj_close: 205.17,
    },
    {
      date: "2025-07-01",
      open: 206.67,
      high: 210.19,
      low: 206.14,
      close: 207.82,
      volume: 78788900,
      adj_close: 207.82,
    },
    {
      date: "2025-07-02",
      open: 208.91,
      high: 213.34,
      low: 208.14,
      close: 212.44,
      volume: 67941800,
      adj_close: 212.44,
    },
    {
      date: "2025-07-03",
      open: 212.15,
      high: 214.65,
      low: 211.81,
      close: 213.55,
      volume: 34955800,
      adj_close: 213.55,
    },
    {
      date: "2025-07-07",
      open: 212.68,
      high: 216.23,
      low: 208.8,
      close: 209.95,
      volume: 50229000,
      adj_close: 209.95,
    },
    {
      date: "2025-07-08",
      open: 210.1,
      high: 211.43,
      low: 208.45,
      close: 210.01,
      volume: 42848900,
      adj_close: 210.01,
    },
    {
      date: "2025-07-09",
      open: 209.53,
      high: 211.33,
      low: 207.22,
      close: 211.14,
      volume: 48749400,
      adj_close: 211.14,
    },
    {
      date: "2025-07-10",
      open: 210.51,
      high: 213.48,
      low: 210.03,
      close: 212.41,
      volume: 44443600,
      adj_close: 212.41,
    },
    {
      date: "2025-07-11",
      open: 210.57,
      high: 212.13,
      low: 209.86,
      close: 211.16,
      volume: 39765800,
      adj_close: 211.16,
    },
    {
      date: "2025-07-14",
      open: 209.93,
      high: 210.91,
      low: 207.54,
      close: 208.62,
      volume: 38840100,
      adj_close: 208.62,
    },
    {
      date: "2025-07-15",
      open: 209.22,
      high: 211.89,
      low: 208.92,
      close: 209.11,
      volume: 42296300,
      adj_close: 209.11,
    },
    {
      date: "2025-07-16",
      open: 210.3,
      high: 212.4,
      low: 208.64,
      close: 210.16,
      volume: 47490500,
      adj_close: 210.16,
    },
    {
      date: "2025-07-17",
      open: 210.57,
      high: 211.8,
      low: 209.59,
      close: 210.02,
      volume: 48068100,
      adj_close: 210.02,
    },
    {
      date: "2025-07-18",
      open: 210.87,
      high: 211.79,
      low: 209.7,
      close: 211.18,
      volume: 48974600,
      adj_close: 211.18,
    },
    {
      date: "2025-07-21",
      open: 212.1,
      high: 215.78,
      low: 211.63,
      close: 212.48,
      volume: 51377400,
      adj_close: 212.48,
    },
    {
      date: "2025-07-22",
      open: 213.14,
      high: 214.95,
      low: 212.23,
      close: 214.4,
      volume: 46404100,
      adj_close: 214.4,
    },
    {
      date: "2025-07-23",
      open: 215,
      high: 215.15,
      low: 212.41,
      close: 214.15,
      volume: 46913800,
      adj_close: 214.15,
    },
    {
      date: "2025-07-24",
      open: 213.9,
      high: 215.69,
      low: 213.53,
      close: 214.41,
      volume: 13295981,
      adj_close: 214.41,
    },
  ],
  metadata: {
    provider: "yahoo_finance",
    data_delay: "unknown",
    market_state: "REGULAR",
    request_params: {
      period: "1mo",
      interval: "1d",
      start_date: null,
      end_date: null,
    },
  },
};

const chartData = [
  {
    date: "2024-07-01",
    AAPL: 154.32,
  },
  {
    date: "2024-07-02",
    AAPL: 236.74,
  },
  {
    date: "2024-07-03",
    AAPL: 134.47,
  },
  {
    date: "2024-07-04",
    AAPL: 236.92,
  },
  {
    date: "2024-07-05",
    AAPL: 152.67,
  },
  {
    date: "2024-07-06",
    AAPL: 136.51,
  },
  {
    date: "2024-07-07",
    AAPL: 214.3,
  },
  {
    date: "2024-07-08",
    AAPL: 259.04,
  },
  {
    date: "2024-07-09",
    AAPL: 241.52,
  },
  {
    date: "2024-07-10",
    AAPL: 146.8,
  },
  {
    date: "2024-07-11",
    AAPL: 156.12,
  },
  {
    date: "2024-07-12",
    AAPL: 191.58,
  },
  {
    date: "2024-07-13",
    AAPL: 232.07,
  },
  {
    date: "2024-07-14",
    AAPL: 170.46,
  },
  {
    date: "2024-07-15",
    AAPL: 151.26,
  },
  {
    date: "2024-07-16",
    AAPL: 278.73,
  },
  {
    date: "2024-07-17",
    AAPL: 264.1,
  },
  {
    date: "2024-07-18",
    AAPL: 255.66,
  },
  {
    date: "2024-07-19",
    AAPL: 269.79,
  },
  {
    date: "2024-07-20",
    AAPL: 147.49,
  },
  {
    date: "2024-07-21",
    AAPL: 208.51,
  },
  {
    date: "2024-07-22",
    AAPL: 123.1,
  },
  {
    date: "2024-07-23",
    AAPL: 140.71,
  },
  {
    date: "2024-07-24",
    AAPL: 152.09,
  },
  {
    date: "2024-07-25",
    AAPL: 163.66,
  },
  {
    date: "2024-07-26",
    AAPL: 126.26,
  },
  {
    date: "2024-07-27",
    AAPL: 133.39,
  },
  {
    date: "2024-07-28",
    AAPL: 254.25,
  },
  {
    date: "2024-07-29",
    AAPL: 249.53,
  },
  {
    date: "2024-07-30",
    AAPL: 250.05,
  },
  {
    date: "2024-07-31",
    AAPL: 246.4,
  },
  {
    date: "2024-08-01",
    AAPL: 164.44,
  },
  {
    date: "2024-08-02",
    AAPL: 133.08,
  },
  {
    date: "2024-08-03",
    AAPL: 245.01,
  },
  {
    date: "2024-08-04",
    AAPL: 137.05,
  },
  {
    date: "2024-08-05",
    AAPL: 205.91,
  },
  {
    date: "2024-08-06",
    AAPL: 236.9,
  },
  {
    date: "2024-08-07",
    AAPL: 203.67,
  },
  {
    date: "2024-08-08",
    AAPL: 130.12,
  },
  {
    date: "2024-08-09",
    AAPL: 215.74,
  },
  {
    date: "2024-08-10",
    AAPL: 176.47,
  },
  {
    date: "2024-08-11",
    AAPL: 177.6,
  },
  {
    date: "2024-08-12",
    AAPL: 255.63,
  },
  {
    date: "2024-08-13",
    AAPL: 271.37,
  },
  {
    date: "2024-08-14",
    AAPL: 244.01,
  },
  {
    date: "2024-08-15",
    AAPL: 218.88,
  },
  {
    date: "2024-08-16",
    AAPL: 268.24,
  },
  {
    date: "2024-08-17",
    AAPL: 239.63,
  },
  {
    date: "2024-08-18",
    AAPL: 227.03,
  },
  {
    date: "2024-08-19",
    AAPL: 141.64,
  },
  {
    date: "2024-08-20",
    AAPL: 172.9,
  },
  {
    date: "2024-08-21",
    AAPL: 262.64,
  },
  {
    date: "2024-08-22",
    AAPL: 149.88,
  },
  {
    date: "2024-08-23",
    AAPL: 160.45,
  },
  {
    date: "2024-08-24",
    AAPL: 165.22,
  },
  {
    date: "2024-08-25",
    AAPL: 198.83,
  },
  {
    date: "2024-08-26",
    AAPL: 251.36,
  },
  {
    date: "2024-08-27",
    AAPL: 185.89,
  },
  {
    date: "2024-08-28",
    AAPL: 194.89,
  },
  {
    date: "2024-08-29",
    AAPL: 228.08,
  },
  {
    date: "2024-08-30",
    AAPL: 234.7,
  },
  {
    date: "2024-08-31",
    AAPL: 156.75,
  },
  {
    date: "2024-09-01",
    AAPL: 192.6,
  },
  {
    date: "2024-09-02",
    AAPL: 135.49,
  },
  {
    date: "2024-09-03",
    AAPL: 261.07,
  },
  {
    date: "2024-09-04",
    AAPL: 187.79,
  },
  {
    date: "2024-09-05",
    AAPL: 148.67,
  },
  {
    date: "2024-09-06",
    AAPL: 204.69,
  },
  {
    date: "2024-09-07",
    AAPL: 155.73,
  },
  {
    date: "2024-09-08",
    AAPL: 211.37,
  },
  {
    date: "2024-09-09",
    AAPL: 225.38,
  },
  {
    date: "2024-09-10",
    AAPL: 127.86,
  },
  {
    date: "2024-09-11",
    AAPL: 216.09,
  },
  {
    date: "2024-09-12",
    AAPL: 134.93,
  },
  {
    date: "2024-09-13",
    AAPL: 228.62,
  },
  {
    date: "2024-09-14",
    AAPL: 259.83,
  },
  {
    date: "2024-09-15",
    AAPL: 160.66,
  },
  {
    date: "2024-09-16",
    AAPL: 157.7,
  },
  {
    date: "2024-09-17",
    AAPL: 164.98,
  },
  {
    date: "2024-09-18",
    AAPL: 166.38,
  },
  {
    date: "2024-09-19",
    AAPL: 168.18,
  },
  {
    date: "2024-09-20",
    AAPL: 155.81,
  },
  {
    date: "2024-09-21",
    AAPL: 233.69,
  },
  {
    date: "2024-09-22",
    AAPL: 249.63,
  },
  {
    date: "2024-09-23",
    AAPL: 257.03,
  },
  {
    date: "2024-09-24",
    AAPL: 220.27,
  },
  {
    date: "2024-09-25",
    AAPL: 251.08,
  },
  {
    date: "2024-09-26",
    AAPL: 258.49,
  },
  {
    date: "2024-09-27",
    AAPL: 135.32,
  },
  {
    date: "2024-09-28",
    AAPL: 147.62,
  },
];

export function Asset() {
  return (
    <div className="flex h-auto w-full max-w-[1180px] flex-col gap-8 p-8">
      <PathLink />
      <HeaderAsset />
      <div className="flex items-start gap-8">
        <div className="flex flex-col gap-8">
          <MarketChart
            title={response.symbol}
            description="Variação de preço"
            chartData={chartData}
          />
          <AssetTabs />
        </div>
        <div className="flex flex-col gap-4">
          <MarketDataCard /> <FundamentalsDataCard />
        </div>
      </div>
    </div>
  );
}

function HeaderAsset() {
  return (
    <div className="flex justify-between">
      <div className="flex flex-col gap-3">
        <h1 className="text-foreground/80 text-3xl font-medium">{`${response.company_name} (${response.symbol})`}</h1>
        <p className="text-muted-foreground flex items-center pl-1 text-base">
          {"Ação"} <Dot />
          {response.currency}
          <Dot />
          {"NASDAQ"}
        </p>
      </div>
      <div className="flex flex-col items-end gap-2">
        <div className="flex gap-3">
          <p className="text-foreground/80 text-4xl font-semibold">
            {formatPrice(response.current_price, response.currency)}
          </p>
          <p
            className={`${response.change_percent > 0 ? "bg-green-card" : "bg-red-card"} text-primary-foreground flex items-center rounded-[8px] px-2 text-lg font-medium`}
          >
            {response.change_percent > 0 ? <ArrowUp /> : <ArrowDown />}
            {response.change_percent}%
          </p>
          <p
            className={`${response.change_percent > 0 ? "text-green-card" : "text-red-card"} flex h-full items-center text-lg font-medium`}
          >
            {formatChange(response.change, false)} Hoje
          </p>
        </div>
        <p className="text-muted-foreground text-base">
          {formatDate(response.last_updated)}
        </p>
      </div>
    </div>
  );
}

function MarketDataCard() {
  return (
    <Card className="w-[300px] flex-none gap-0 p-0">
      <CardHeader className="border-border flex items-center border-b-1 py-5">
        <CardTitle className="text-base">Dados de Mercado</CardTitle>
      </CardHeader>
      <ul className="flex flex-col p-5 text-xs">
        <li className="border-border text-muted-foreground flex items-center justify-between border-b py-4">
          Abertura{" "}
          <span className="text-foreground text-xs font-medium">
            {formatPrice(234.5, "USD")}
          </span>
        </li>
        <li className="border-border text-muted-foreground flex items-center justify-between border-b py-4">
          Ultimo Fechamento
          <span className="text-foreground text-xs font-medium">
            {formatPrice(response.previous_close, "USD")}
          </span>
        </li>
        <li className="border-border text-muted-foreground flex items-center justify-between border-b py-4">
          {"Variação de hoje(%)"}
          <span
            className={`${response.change_percent > 0 ? "text-green-card" : "text-red-card"} text-xs font-medium`}
          >
            {formatChange(response.change_percent)}
          </span>
        </li>
        <li className="border-border text-muted-foreground flex items-center justify-between border-b py-4">
          Variações de hoje
          <span className="text-foreground text-xs font-medium">
            {`${formatPrice(231.8, "USD")} - ${formatPrice(239.5, "USD")}`}
          </span>
        </li>
        <li className="border-border text-muted-foreground flex items-center justify-between border-b py-4">
          Variações do ano
          <span className="text-foreground text-xs font-medium">
            {`${formatPrice(response.fundamentals.fifty_two_week_low, "USD")} - ${formatPrice(response.fundamentals.fifty_two_week_high, "USD")}`}
          </span>
        </li>
        <li className="border-border text-muted-foreground flex items-center justify-between border-b py-4">
          Volume
          <span className="text-foreground text-xs font-medium">
            {formatNumber(response.volume)}
          </span>
        </li>
        <li className="text-muted-foreground flex items-center justify-between py-4">
          Volume médio
          <span className="text-foreground text-xs font-medium">
            {formatNumber(response.avg_volume)}
          </span>
        </li>
      </ul>
    </Card>
  );
}

function FundamentalsDataCard() {
  return (
    <Card className="w-[300px] flex-none gap-0 p-0">
      <CardHeader className="border-border flex items-center border-b-1 py-5">
        <CardTitle className="text-base">Indicadores Fundamentalista</CardTitle>
      </CardHeader>
      <ul className="flex flex-col p-5 text-xs">
        <li className="border-border text-muted-foreground flex items-center justify-between border-b py-4">
          Valor de Mercado{" "}
          <span className="text-foreground text-xs font-medium">
            {formatNumber(response.fundamentals.market_cap)}
          </span>
        </li>
        <li className="border-border text-muted-foreground flex items-center justify-between border-b py-4">
          Dividend Yield
          <span className="text-foreground text-xs font-medium">
            {`${response.fundamentals.dividend_yield.toLocaleString("pt-BR")}%`}
          </span>
        </li>
        <li className="border-border text-muted-foreground flex items-center justify-between border-b py-4">
          Índice P/L
          <span className="text-foreground text-xs font-medium">
            {`${response.fundamentals.pe_ratio.toLocaleString("pt-BR")}%`}
          </span>
        </li>
        <li className="border-border text-muted-foreground flex items-center justify-between border-b py-4">
          ROE
          <span className="text-foreground text-xs font-medium">
            {`${response.fundamentals.roe.toLocaleString("pt-BR")}%`}
          </span>
        </li>
        <li className="text-muted-foreground flex items-center justify-between py-4">
          Margem Líquida
          <span className="text-foreground text-xs font-medium">
            {formatNumber(response.fundamentals.market_cap)}
          </span>
        </li>
      </ul>
    </Card>
  );
}

function AssetTabs() {
  return (
    <Tabs defaultValue="sobre" className="w-full gap-6">
      <TabsList className="border-border flex h-auto w-full justify-start rounded-none border-b-2 bg-transparent p-0">
        <TabsTrigger
          value="sobre"
          className="text-muted-foreground hover:text-primary data-[state=active]:text-primary data-[state=active]:dark:text-primary data-[state=active]:dark:border-primary border-primary hover:dark:text-primary flex-none cursor-pointer rounded-none border-0 px-5 py-3 data-[state=active]:-mb-[2px] data-[state=active]:border-b-2 data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:dark:bg-transparent"
        >
          Sobre
        </TabsTrigger>
        <TabsTrigger
          value="noticias"
          className="text-muted-foreground hover:text-primary data-[state=active]:text-primary data-[state=active]:dark:text-primary data-[state=active]:dark:border-primary border-primary hover:dark:text-primary flex-none cursor-pointer rounded-none border-0 px-6 py-3 data-[state=active]:-mb-[2px] data-[state=active]:border-b-2 data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:dark:bg-transparent"
        >
          Notícias
        </TabsTrigger>
        <TabsTrigger
          value="historico-proventos"
          className="text-muted-foreground hover:text-primary data-[state=active]:text-primary data-[state=active]:dark:text-primary data-[state=active]:dark:border-primary border-primary hover:dark:text-primary flex-none cursor-pointer rounded-none border-0 px-5 py-3 data-[state=active]:-mb-[2px] data-[state=active]:border-b-2 data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:dark:bg-transparent"
        >
          Histórico de Proventos
        </TabsTrigger>
      </TabsList>
      <TabsContent value="sobre" className="flex flex-col gap-2">
        <h3 className="text-foreground/80 text-lg font-semibold">
          Sobre {response.company_name}
        </h3>
        <p className="text-muted-foreground whitespace-pre-line">
          Apple é uma empresa multinacional norte-americana que tem o objetivo
          de projetar e comercializar produtos eletrônicos de consumo, software
          de computador e computadores pessoais. Os produtos de hardware mais
          conhecidos da empresa incluem a linha de computadores Macintosh, iPod,
          iPhone, iPad, Apple TV e o Apple Watch. Os softwares incluem o sistema
          operacional macOS, o navegador de mídia iTunes, suíte de software
          multimídia e criatividade iLife, suíte de software de produtividade
          iWork, Aperture, um pacote de fotografia profissional, Final Cut
          Studio, uma suíte de vídeo profissional, produtos de software, Logic
          Studio, um conjunto de ferramentas de produção musical, navegador
          Safari e o iOS, um sistema operacional móvel. Em agosto de 2010, a
          empresa operava 301 lojas de varejo em dez países, e uma loja online
          onde os produtos de hardware e software são vendidos. Para além das
          Apple Store, a empresa possui as Apple Shops e as Apple Premium
          Resellers. As primeiras são pequenas áreas exclusivas à marca,
          devidamente sinalizadas e inseridas em operadores multimarca.
        </p>
      </TabsContent>
      <TabsContent value="password">Change your password here.</TabsContent>
    </Tabs>
  );
}
