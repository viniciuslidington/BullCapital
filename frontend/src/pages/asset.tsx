import { MarketChart } from "@/components/features/markets-chart/market-chart";
import { PathLink } from "@/components/ui/path-link";
import {
  formatChange,
  formatDate,
  formatNumber,
  formatPrice,
} from "@/lib/utils";
import {
  AlertCircle,
  ArrowDown,
  ArrowUp,
  ChevronUp,
  Dot,
  Newspaper,
} from "lucide-react";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TabsContent } from "@radix-ui/react-tabs";
import { useLocation } from "react-router-dom";
import type { CompanyOfficers, TickerBasicInfoResponse } from "@/types/ticker";
import { useTickerInfo } from "@/hooks/queries/useticker";
import { Skeleton } from "@/components/ui/skeleton";
import { useDataCard } from "@/hooks/utils/usedatacard";
import { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { SECTOR_TRANSLATE } from "@/data/sector-data";
import type { Setores } from "@/types/category";
import { useNews } from "@/hooks/queries/usenews";
import { useDividends } from "@/hooks/queries/usedividends";

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
  const tickerSymbol = useLocation().pathname.replace("/", "");
  const { data, isError, isLoading, isFetching } = useTickerInfo(tickerSymbol);
  const fetchState = { isError, isLoading, isFetching };

  const noSkeleton = !isError && !isLoading;

  const {
    marketData,
    valuation,
    rentability,
    eficiencyAndCashflow,
    debtAndSolvency,
    dividends,
    shareholdingAndProfit,
    analystData,
  } = useDataCard(tickerSymbol);

  return (
    <div className="flex h-auto w-full max-w-[1180px] flex-col gap-8 p-8">
      <PathLink />
      <HeaderAsset
        response={data as TickerBasicInfoResponse}
        fetchState={fetchState}
        tickerSymbol={tickerSymbol}
      />
      <div className="flex items-start gap-8">
        <div className="flex flex-1 flex-col gap-8">
          <MarketChart
            title={tickerSymbol}
            description="Variação de preço"
            chartData={chartData}
          />
          <AssetTabs ticker={tickerSymbol} />
        </div>
        <div className="flex flex-col gap-4">
          <MarketDataCard
            title={"Dados de Mercado"}
            itens={marketData}
            currency={data?.currency ?? "USD"}
            fetchState={fetchState}
            openByDefault
          />
          <MarketDataCard
            title={"Indicadores de Valuation"}
            itens={valuation}
            currency={data?.currency ?? "USD"}
            fetchState={fetchState}
            openByDefault
          />
          {noSkeleton && (
            <MarketDataCard
              title={"Dividendos"}
              itens={dividends}
              currency={data?.currency ?? ""}
              fetchState={fetchState}
            />
          )}
          {noSkeleton && (
            <MarketDataCard
              title={"Participação e Lucro"}
              itens={shareholdingAndProfit}
              currency={data?.currency ?? ""}
              fetchState={fetchState}
            />
          )}
          {noSkeleton && (
            <MarketDataCard
              title={"Rentabilidade"}
              itens={rentability}
              currency={data?.currency ?? ""}
              fetchState={fetchState}
            />
          )}
          {noSkeleton && (
            <MarketDataCard
              title={"Eficiência e Fluxo de Caixa"}
              itens={eficiencyAndCashflow}
              currency={data?.currency ?? ""}
              fetchState={fetchState}
            />
          )}
          {noSkeleton && (
            <MarketDataCard
              title={"Débito e Solvência"}
              itens={debtAndSolvency}
              currency={data?.currency ?? ""}
              fetchState={fetchState}
            />
          )}
          {noSkeleton && (
            <MarketDataCard
              title={"Risco e Opinião de Mercado"}
              itens={analystData}
              currency={data?.currency ?? ""}
              fetchState={fetchState}
            />
          )}
        </div>
      </div>
      {isError && (
        <div className="text-destructive bg-card/60 absolute top-[calc(100vh/2)] left-1/2 flex -translate-x-1/2 items-center gap-2 rounded-xl border p-6 shadow-lg backdrop-blur-lg">
          <AlertCircle /> <p>Falha ao carregar "{tickerSymbol}"</p>
        </div>
      )}
    </div>
  );
}

function HeaderAsset({
  response,
  fetchState,
  tickerSymbol,
}: {
  response: TickerBasicInfoResponse;
  tickerSymbol: string;
  fetchState: {
    isLoading: boolean;
    isFetching: boolean;
    isError: boolean;
  };
}) {
  const { isLoading, isError } = fetchState;
  if (isLoading || response === null || response === undefined || isError)
    return (
      <div
        className={`flex h-[72px] flex-col justify-between gap-3 ${isError ? "blur-sm" : ""}`}
      >
        <div className="flex justify-between">
          <Skeleton animation={!isError} className="h-8 w-[320px]" />
          <Skeleton animation={!isError} className="h-9 w-[345px]" />
        </div>
        <div className="flex justify-between">
          <Skeleton animation={!isError} className="h-6 w-[180px]" />
          <Skeleton animation={!isError} className="h-6 w-[170px]" />
        </div>
      </div>
    );

  return (
    <div className="flex max-w-full justify-between gap-10">
      <div className="flex w-full min-w-0 flex-grow flex-col gap-3">
        <span className="flex items-center gap-1">
          <h1 className="text-foreground/80 truncate text-3xl font-medium">
            {response.longName ?? ""}
          </h1>{" "}
          <p className="text-foreground/80 text-3xl font-medium">{`(${tickerSymbol})`}</p>
        </span>
        <p className="text-muted-foreground flex items-center pl-1 text-base">
          {response.type ?? ""}
          {response.currency !== "" && <Dot />}
          {response.currency ?? 0}
          <Dot />
          {response.fullExchangeName ?? ""}
        </p>
      </div>
      <div className="flex flex-shrink-0 flex-col items-end gap-2">
        <div className="flex gap-3">
          <p
            className={`text-foreground/80 text-4xl font-semibold ${fetchState.isFetching ? "opacity-80" : ""}`}
          >
            {formatPrice(
              response.priceAndVariation.currentPrice ?? 0,
              response.currency ?? 0,
            )}
          </p>
          <p
            className={`${(response.priceAndVariation.regularMarketChangePercent ?? 0) > 0 ? "bg-green-card" : "bg-red-card"} text-primary-foreground flex items-center rounded-[8px] px-2 text-lg font-medium ${fetchState.isFetching ? "opacity-80" : ""}`}
          >
            {(response.priceAndVariation.regularMarketChangePercent ?? 0) >
            0 ? (
              <ArrowUp />
            ) : (
              <ArrowDown />
            )}
            {response.priceAndVariation.regularMarketChangePercent.toFixed(2) ??
              0}
            %
          </p>
          <p
            className={`${(response.priceAndVariation.regularMarketChangePercent ?? 0) > 0 ? "text-green-card" : "text-red-card"} flex h-full items-center text-lg font-medium ${fetchState.isFetching ? "opacity-80" : ""}`}
          >
            {formatChange(
              response.priceAndVariation.regularMarketChange ?? 0,
              false,
            )}{" "}
            Hoje
          </p>
        </div>
        <p
          className={`text-muted-foreground text-base ${fetchState.isFetching ? "opacity-80" : ""}`}
        >
          {formatDate(response.timestamp ?? "")}
        </p>
      </div>
    </div>
  );
}

function MarketDataCard({
  itens,
  currency,
  fetchState,
  title,
  openByDefault = false,
}: {
  itens: { title: string; value: string | number | undefined; unit: string }[];
  currency: string;
  fetchState: {
    isLoading: boolean;
    isFetching: boolean;
    isError: boolean;
  };
  title: string;
  openByDefault?: boolean;
}) {
  const [isOpen, setIsOpen] = useState(openByDefault);
  if (
    fetchState.isLoading ||
    itens === null ||
    itens === undefined ||
    fetchState.isError
  )
    return (
      <Skeleton
        animation={!fetchState.isError}
        className={`${fetchState.isError ? "blur-sm" : ""} h-[450px] w-[300px] rounded-xl`}
      />
    );

  const itensFiltrados = itens?.filter(
    ({ value, title }) =>
      value !== null && (value !== 0 || title === "Variação de hoje(%)"),
  );
  if (itensFiltrados.length === 0) return;

  return (
    <Card className="bg-card/60 w-[300px] flex-none gap-0 p-0">
      <CardHeader className="flex items-center justify-between py-3">
        <CardTitle className="text-base">{title}</CardTitle>
        <ChevronUp
          onClick={() => setIsOpen(!isOpen)}
          className={`${isOpen ? "" : "rotate-180"} size-6 cursor-pointer transition-transform duration-300 ease-out`}
        />
      </CardHeader>
      <div
        className={`overflow-hidden transition-all delay-0 duration-500 ease-in-out ${
          isOpen ? "max-h-[1000px]" : "max-h-0"
        }`}
      >
        <ul className="divide-border border-border flex flex-col divide-y border-t-1 p-5 text-xs">
          {itensFiltrados.map(({ title, value, unit }) => (
            <li
              key={title}
              className="text-muted-foreground flex items-center justify-between py-4"
            >
              {title}
              <span className="text-foreground text-xs font-medium">
                {unit === "currency" && formatPrice(value as number, currency)}
                {unit === "largeNumber" && formatNumber(value as number)}
                {unit === "percent" && formatChange(value as number)}
                {unit === "string" && value}
              </span>
            </li>
          ))}
        </ul>
      </div>
    </Card>
  );
}

const infoRowsConfig = [
  { label: "Nome", dataKey: "longName" },
  {
    label: "Sumário",
    dataKey: "business_summary",
    className: "whitespace-normal",
  },
  {
    label: "Setor",
    dataKey: "sector",
    // 1. O formatter agora aceita 'unknown' e verifica o tipo internamente.
    formatter: (value: unknown) => {
      if (typeof value !== "string") return null;
      return SECTOR_TRANSLATE[value as Setores];
    },
  },
  { label: "Indústria", dataKey: "industry" },
  { label: "Site", dataKey: "website" },
  { label: "País", dataKey: "country" },
  { label: "Bolsa", dataKey: "fullExchangeName" },
  { label: "Num. Empregados", dataKey: "employees" },
  {
    label: "Maiores Acionistas",
    dataKey: "companyOfficers",
    // 2. O mesmo para o formatter de acionistas: aceita 'unknown' e verifica se é um array.
    formatter: (value: unknown) => {
      // Adicionamos uma verificação de tipo (type guard)
      if (!Array.isArray(value)) {
        return null; // Retorna nulo se não for um array, evitando o erro.
      }

      // Agora o TypeScript sabe que 'value' é um array e o código é seguro
      return (value as CompanyOfficers[]).map((item) => (
        <span key={item.name} className="flex items-center">
          <Dot className="mr-1 h-4 w-4 shrink-0" /> {item.name}
        </span>
      ));
    },
  },
];

// O resto do seu componente AssetTabs permanece igual...
export function AssetTabs({ ticker }: { ticker: string }) {
  const { data, isLoading, isError } = useTickerInfo(ticker);
  const {
    data: news,
    isLoading: newsLoading,
    isError: newsError,
  } = useNews(ticker);
  const { data: dividends } = useDividends(ticker);
  const isSkeleton = !data || isError || isLoading;
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
          value="news"
          className="text-muted-foreground hover:text-primary data-[state=active]:text-primary data-[state=active]:dark:text-primary data-[state=active]:dark:border-primary border-primary hover:dark:text-primary flex-none cursor-pointer rounded-none border-0 px-6 py-3 data-[state=active]:-mb-[2px] data-[state=active]:border-b-2 data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:dark:bg-transparent"
        >
          Notícias
        </TabsTrigger>
        <TabsTrigger
          value="dividends"
          className="text-muted-foreground hover:text-primary data-[state=active]:text-primary data-[state=active]:dark:text-primary data-[state=active]:dark:border-primary border-primary hover:dark:text-primary flex-none cursor-pointer rounded-none border-0 px-5 py-3 data-[state=active]:-mb-[2px] data-[state=active]:border-b-2 data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:dark:bg-transparent"
        >
          Histórico de Proventos
        </TabsTrigger>
      </TabsList>

      <TabsContent value="sobre" className={`${isError ? "blur-sm" : ""}`}>
        {isSkeleton ? (
          <Skeleton
            animation={!isError}
            className="h-[700px] w-full rounded-xl"
          />
        ) : (
          <Table className="bg-card/60">
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead className="w-[180px]">Sobre</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {infoRowsConfig.map(
                ({ label, dataKey, formatter, className }) => {
                  const value = data?.[dataKey as keyof typeof data];
                  if (!value || (Array.isArray(value) && value.length === 0)) {
                    return null;
                  }
                  return (
                    <TableRow key={label}>
                      <TableCell className="flex font-medium">
                        {label}
                      </TableCell>
                      <TableCell className={className}>
                        {formatter ? formatter(value) : String(value)}
                      </TableCell>
                    </TableRow>
                  );
                },
              )}
            </TableBody>
          </Table>
        )}
      </TabsContent>
      <TabsContent value="news" className={`${isError ? "blur-sm" : ""}`}>
        {newsLoading ? (
          <Skeleton
            animation={!isError}
            className="h-[700px] w-full rounded-xl"
          />
        ) : (
          <div className="flex flex-col gap-4">
            {news?.map((item) => (
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-card/60 text-card-foreground hover:bg-accent flex gap-4 rounded-xl border p-4 shadow-sm transition-colors"
              >
                {item.thumbnail ? (
                  // Se a thumbnail existir, mostra a imagem
                  <img
                    src={item.thumbnail}
                    alt={`Thumbnail para a notícia: ${item.title}`}
                    className="bg-muted h-28 w-28 shrink-0 rounded-md object-cover"
                  />
                ) : (
                  <div className="bg-muted flex h-28 w-28 shrink-0 items-center justify-center rounded-md">
                    <Newspaper className="text-muted-foreground h-10 w-10" />
                  </div>
                )}

                <div className="flex flex-col">
                  <h3 className="line-clamp-2 leading-tight font-medium">
                    {item.title}
                  </h3>
                  <p className="text-muted-foreground mt-1 line-clamp-3 text-sm">
                    {item.summary}
                  </p>
                  <time className="text-muted-foreground mt-auto pt-2 text-xs">
                    {formatDate(item.date)}
                  </time>
                </div>
              </a>
            ))}
          </div>
        )}
      </TabsContent>
      <TabsContent value="dividends" className={`${isError ? "blur-sm" : ""}`}>
        {newsLoading ? (
          <Skeleton
            animation={!isError}
            className="h-[700px] w-full rounded-xl"
          />
        ) : (
          <div className="flex flex-col gap-4"></div>
        )}
      </TabsContent>
    </Tabs>
  );
}
