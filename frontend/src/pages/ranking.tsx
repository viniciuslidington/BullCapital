import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { CategoriasType } from "@/types/assets";
import {
  Building2,
  ChartNoAxesCombined,
  Coins,
  Earth,
  Layers,
} from "lucide-react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { categoriaData } from "@/data/categoria-data";
import { PathLink } from "@/components/ui/path-link";
import { QuestionMark } from "@/components/ui/question-mark";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatNumber } from "@/lib/utils";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { useAddParams } from "@/hooks/utils/useaddparams";

export function Ranking() {
  const [searchParams] = useSearchParams();
  const categoria =
    (searchParams.get("categoria") as CategoriasType) || "acoes";

  return (
    <div className="flex h-auto w-full max-w-[1180px] flex-col gap-8 p-8">
      <PathLink />
      <h1 className="text-foreground/80 -mb-4 flex items-center gap-2 text-3xl font-semibold">
        <ChartNoAxesCombined className="h-8 w-8" /> Ranking de{" "}
        {categoriaData[categoria].shortTitle}
        <span className="pt-1">
          <QuestionMark
            dataIndex={categoria}
            dataType="categoryDescription"
            delay={50}
          />
        </span>
      </h1>
      <div className="-mb-4 flex justify-between">
        <RankingTabs />
        <RankingFilterSelect />
      </div>
      <RankingTable />
      <RankingPagination />
    </div>
  );
}

function RankingTabs() {
  const [searchParams] = useSearchParams();
  const addParams = useAddParams();
  return (
    <Tabs
      defaultValue={searchParams.get("categoria") || "acoes"}
      className="w-full"
      onValueChange={(value) => addParams("categoria", value)}
    >
      <TabsList className="gap-3 bg-transparent">
        <TabsTrigger
          value="acoes"
          className="data-[state=active]:bg-primary data-[state=active]:dark:bg-primary data-[state=active]:text-primary-foreground border-border bg-card hover:bg-muted data-[state=active]:border-primary cursor-pointer border p-4 shadow-sm transition-all duration-150"
        >
          <Coins /> Ações
        </TabsTrigger>
        <TabsTrigger
          value="fiis"
          className="data-[state=active]:bg-primary data-[state=active]:dark:bg-primary data-[state=active]:text-primary-foreground border-border bg-card hover:bg-muted data-[state=active]:border-primary cursor-pointer border p-4 shadow-sm transition-all duration-150"
        >
          <Building2 />
          FIIs
        </TabsTrigger>
        <TabsTrigger
          value="etfs"
          className="data-[state=active]:bg-primary data-[state=active]:dark:bg-primary data-[state=active]:text-primary-foreground border-border bg-card hover:bg-muted data-[state=active]:border-primary cursor-pointer border p-4 shadow-sm transition-all duration-150"
        >
          <Layers />
          ETFs
        </TabsTrigger>
        <TabsTrigger
          value="bdrs"
          className="data-[state=active]:bg-primary data-[state=active]:dark:bg-primary data-[state=active]:text-primary-foreground border-border bg-card hover:bg-muted data-[state=active]:border-primary cursor-pointer border p-4 shadow-sm transition-all duration-150"
        >
          <Earth />
          BDRs
        </TabsTrigger>
      </TabsList>
      <TabsContent value="account">
        Make changes to your account here.
      </TabsContent>
      <TabsContent value="password">Change your password here.</TabsContent>
    </Tabs>
  );
}

function RankingFilterSelect() {
  const [searchParams] = useSearchParams();
  const addParams = useAddParams();
  const filtro = (searchParams.get("filtro") as CategoriasType) || "altas";

  return (
    <Select
      value={filtro}
      onValueChange={(value) => addParams("filtro", value)}
    >
      <SelectTrigger className="bg-card w-[160px] rounded-lg sm:ml-auto sm:flex">
        <SelectValue placeholder="Selecione Filtro" />
      </SelectTrigger>
      <SelectContent className="rounded-xl" align="end">
        <SelectItem value="altas" className="rounded-lg">
          Maiores Altas
        </SelectItem>
        <SelectItem value="baixas" className="rounded-lg">
          Maiores Baixas
        </SelectItem>
        <SelectItem value="ativas" className="rounded-lg">
          Mais Ativas
        </SelectItem>
        <SelectItem value="dividendos" className="rounded-lg">
          Maiores Dividendos
        </SelectItem>
      </SelectContent>
    </Select>
  );
}

const ranking = [
  {
    ticker: "PETR4",
    nome: "Petrobras PN",
    variacao: 1.85, // %
    precoAtual: 37.42, // R$
    roe: 27.1, // %
    pl: 3.2,
    dividendYield: 13.5, // %
    max52Semanas: 39.12, // R$
    valorMercado: 480_000_000_000, // R$
    margemLiquida: 28.6, // %
    currency: "BRL",
  },
  {
    ticker: "ITUB4",
    nome: "Itaú Unibanco PN",
    variacao: 0.95,
    precoAtual: 31.7,
    roe: 20.4,
    pl: 8.3,
    dividendYield: 4.8,
    max52Semanas: 33.8,
    valorMercado: 320_000_000_000,
    margemLiquida: 25.2,
    currency: "BRL",
  },
  {
    ticker: "WEGE3",
    nome: "Weg ON",
    variacao: -0.52,
    precoAtual: 38.1,
    roe: 22.3,
    pl: 32.7,
    dividendYield: 1.8,
    max52Semanas: 42.15,
    valorMercado: 160_000_000_000,
    margemLiquida: 17.6,
    currency: "BRL",
  },
  {
    ticker: "VALE3",
    nome: "Vale ON",
    variacao: 0.12,
    precoAtual: 66.5,
    roe: 35.7,
    pl: 4.9,
    dividendYield: 9.4,
    max52Semanas: 76.3,
    valorMercado: 360_000_000_000,
    margemLiquida: 31.8,
    currency: "BRL",
  },
  {
    ticker: "BBAS3",
    nome: "Banco do Brasil ON",
    variacao: 2.31,
    precoAtual: 53.6,
    roe: 21.6,
    pl: 4.3,
    dividendYield: 9.9,
    max52Semanas: 55.8,
    valorMercado: 150_000_000_000,
    margemLiquida: 24.7,
    currency: "BRL",
  },
  {
    ticker: "PETR4",
    nome: "Petrobras PN",
    variacao: 1.85, // %
    precoAtual: 37.42, // R$
    roe: 27.1, // %
    pl: 3.2,
    dividendYield: 13.5, // %
    max52Semanas: 39.12, // R$
    valorMercado: 480_000_000_000, // R$
    margemLiquida: 28.6, // %
    currency: "BRL",
  },
  {
    ticker: "ITUB4",
    nome: "Itaú Unibanco PN",
    variacao: 0.95,
    precoAtual: 31.7,
    roe: 20.4,
    pl: 8.3,
    dividendYield: 4.8,
    max52Semanas: 33.8,
    valorMercado: 320_000_000_000,
    margemLiquida: 25.2,
    currency: "BRL",
  },
  {
    ticker: "WEGE3",
    nome: "Weg ON",
    variacao: -0.52,
    precoAtual: 38.1,
    roe: 22.3,
    pl: 32.7,
    dividendYield: 1.8,
    max52Semanas: 42.15,
    valorMercado: 160_000_000_000,
    margemLiquida: 17.6,
    currency: "BRL",
  },
  {
    ticker: "VALE3",
    nome: "Vale ON",
    variacao: 0.12,
    precoAtual: 66.5,
    roe: 35.7,
    pl: 4.9,
    dividendYield: 9.4,
    max52Semanas: 76.3,
    valorMercado: 360_000_000_000,
    margemLiquida: 31.8,
    currency: "BRL",
  },
  {
    ticker: "BBAS3",
    nome: "Banco do Brasil ON",
    variacao: 2.31,
    precoAtual: 53.6,
    roe: 21.6,
    pl: 4.3,
    dividendYield: 9.9,
    max52Semanas: 55.8,
    valorMercado: 150_000_000_000,
    margemLiquida: 24.7,
    currency: "BRL",
  },
];

export function RankingTable() {
  const navigate = useNavigate();
  return (
    <Table className="bg-card">
      <TableHeader>
        <TableRow className="hover:bg-transparent">
          <TableHead className="w-[100px]">Ativo</TableHead>
          <TableHead className="text-center">Variação</TableHead>
          <TableHead className="text-center">Preço Atual</TableHead>
          <TableHead className="text-center">ROE</TableHead>
          <TableHead className="text-center">Índice P/L</TableHead>
          <TableHead className="text-center">Dividend Yield</TableHead>
          <TableHead className="text-center">Max 52s</TableHead>
          <TableHead className="text-center">Val. Mercado</TableHead>
          <TableHead className="text-center">Margem Líquida</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {ranking.map((item) => (
          <TableRow key={item.ticker} className="text-foreground/80">
            <TableCell
              className="text-foreground hover:text-primary cursor-pointer font-medium transition-all"
              onClick={() => {
                navigate(`/${item.ticker}`, { state: { from: "ranking" } });
              }}
            >
              {item.ticker}
            </TableCell>
            <TableCell align="center">{item.variacao}</TableCell>
            <TableCell align="center">{item.precoAtual}</TableCell>
            <TableCell align="center">{item.roe}</TableCell>
            <TableCell align="center">{item.pl}</TableCell>
            <TableCell align="center">{item.dividendYield}</TableCell>
            <TableCell align="center">{item.max52Semanas}</TableCell>
            <TableCell align="center">
              {formatNumber(item.valorMercado)}
            </TableCell>
            <TableCell align="center">{item.margemLiquida}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}

export function RankingPagination() {
  return (
    <Pagination className="justify-end">
      <PaginationContent>
        <PaginationItem>
          <PaginationPrevious href="#" />
        </PaginationItem>
        <PaginationItem>
          <PaginationLink href="#">1</PaginationLink>
        </PaginationItem>
        <PaginationItem>
          <PaginationEllipsis />
        </PaginationItem>
        <PaginationItem>
          <PaginationNext href="#" />
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  );
}
