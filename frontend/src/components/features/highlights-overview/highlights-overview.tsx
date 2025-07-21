import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { HighlightsCard } from "./highlights-card";

const mockAcoesBR = {
  emAlta: [
    {
      ticker: "PETR4",
      nome: "Petrobras PN",
      preco: 32.1,
      changePercent: 4.21,
      currency: "BRL",
    },
    {
      ticker: "VALE3",
      nome: "Vale S.A.",
      preco: 74.8,
      changePercent: 3.35,
      currency: "BRL",
    },
    {
      ticker: "BBAS3",
      nome: "Banco do Brasil",
      preco: 56.9,
      changePercent: 2.18,
      currency: "BRL",
    },
    {
      ticker: "SUZB3",
      nome: "Suzano S.A.",
      preco: 53.4,
      changePercent: 2.91,
      currency: "BRL",
    },
    {
      ticker: "JBSS3",
      nome: "JBS S.A.",
      preco: 23.7,
      changePercent: 3.1,
      currency: "BRL",
    },
  ],
  emBaixa: [
    {
      ticker: "MGLU3",
      nome: "Magazine Luiza",
      preco: 2.31,
      changePercent: -4.54,
      currency: "BRL",
    },
    {
      ticker: "LWSA3",
      nome: "Locaweb",
      preco: 5.22,
      changePercent: -3.89,
      currency: "BRL",
    },
    {
      ticker: "CVCB3",
      nome: "CVC Brasil",
      preco: 3.4,
      changePercent: -2.75,
      currency: "BRL",
    },
    {
      ticker: "AMER3",
      nome: "Americanas S.A.",
      preco: 0.95,
      changePercent: -5.1,
      currency: "BRL",
    },
    {
      ticker: "VIIA3",
      nome: "Via Varejo",
      preco: 1.87,
      changePercent: -3.12,
      currency: "BRL",
    },
  ],
  maisNegociados: [
    {
      ticker: "PETR4",
      nome: "Petrobras PN",
      preco: 32.1,
      changePercent: 4.21,
      currency: "BRL",
    },
    {
      ticker: "VALE3",
      nome: "Vale S.A.",
      preco: 74.8,
      changePercent: 3.35,
      currency: "BRL",
    },
    {
      ticker: "ITUB4",
      nome: "Itaú Unibanco PN",
      preco: 28.9,
      changePercent: -1.87,
      currency: "BRL",
    },
    {
      ticker: "BBDC4",
      nome: "Bradesco PN",
      preco: 16.45,
      changePercent: 0.52,
      currency: "BRL",
    },
    {
      ticker: "BBAS3",
      nome: "Banco do Brasil",
      preco: 56.9,
      changePercent: 2.18,
      currency: "BRL",
    },
  ],
  maioresDividendos: [
    {
      ticker: "TAEE11",
      nome: "Taesa Units",
      dividendo: 4.58,
      tipo: "Dividendo",
      dataCom: "2024-12-10",
      dataEx: "2024-12-11",
      dataPagamento: "2024-12-15",
    },
    {
      ticker: "EGIE3",
      nome: "Engie Brasil",
      dividendo: 3.25,
      tipo: "JCP",
      dataCom: "2024-11-25",
      dataEx: "2024-11-26",
      dataPagamento: "2024-11-30",
    },
    {
      ticker: "TRPL4",
      nome: "Transmissão Paulista PN",
      dividendo: 2.85,
      tipo: "Dividendo",
      dataCom: "2024-12-05",
      dataEx: "2024-12-06",
      dataPagamento: "2024-12-10",
    },
    {
      ticker: "CPLE6",
      nome: "Copel PN B",
      dividendo: 1.7,
      tipo: "JCP",
      dataCom: "2024-12-18",
      dataEx: "2024-12-19",
      dataPagamento: "2024-12-20",
    },
    {
      ticker: "BBSE3",
      nome: "BB Seguridade",
      dividendo: 2.45,
      tipo: "Dividendo",
      dataCom: "2024-11-28",
      dataEx: "2024-11-29",
      dataPagamento: "2024-12-01",
    },
  ],
};

export function HighlightsOverview() {
  return (
    <div className="flex w-full items-center gap-5">
      <Tabs defaultValue="acoes" className="w-full">
        <TabsList className="gap-2">
          <p className="text-muted-foreground dark:text-foreground mr-2 font-semibold">
            DESTAQUES
          </p>
          <TabsTrigger
            value="acoes"
            className="data-[state=active]:bg-primary data-[state=active]:dark:bg-primary data-[state=active]:text-primary-foreground hover:text-primary dark:hover:text-primary cursor-pointer"
          >
            Ações
          </TabsTrigger>
          <TabsTrigger
            value="fiis"
            className="data-[state=active]:bg-primary data-[state=active]:dark:bg-primary data-[state=active]:text-primary-foreground hover:text-primary dark:hover:text-primary cursor-pointer"
          >
            FIIs
          </TabsTrigger>
          <TabsTrigger
            value="etfs"
            className="data-[state=active]:bg-primary data-[state=active]:dark:bg-primary data-[state=active]:text-primary-foreground hover:text-primary dark:hover:text-primary cursor-pointer"
          >
            ETFs
          </TabsTrigger>
          <TabsTrigger
            value="bdrs"
            className="data-[state=active]:bg-primary data-[state=active]:dark:bg-primary data-[state=active]:text-primary-foreground hover:text-primary dark:hover:text-primary cursor-pointer"
          >
            BDRs
          </TabsTrigger>
        </TabsList>
        <TabsContent value="acoes" className="flex gap-5">
          <HighlightsCard title="Altas" items={mockAcoesBR.emAlta} />
          <HighlightsCard title="Baixas" items={mockAcoesBR.emBaixa} />
          <HighlightsCard
            title="Mais Ativas"
            items={mockAcoesBR.maisNegociados}
          />
          <HighlightsCard title="Dividendos" items={mockAcoesBR.emAlta} />
        </TabsContent>
        <TabsContent value="fiis" className="flex gap-5">
          <HighlightsCard title="Altas" items={mockAcoesBR.emAlta} />
          <HighlightsCard title="Baixas" items={mockAcoesBR.emBaixa} />
          <HighlightsCard
            title="Mais Ativas"
            items={mockAcoesBR.maisNegociados}
          />
          <HighlightsCard title="Dividendos" items={mockAcoesBR.emAlta} />
        </TabsContent>
        <TabsContent value="etfs" className="flex gap-5">
          <HighlightsCard title="Altas" items={mockAcoesBR.emAlta} />
          <HighlightsCard title="Baixas" items={mockAcoesBR.emBaixa} />
          <HighlightsCard
            title="Mais Ativas"
            items={mockAcoesBR.maisNegociados}
          />
          <HighlightsCard title="Dividendos" items={mockAcoesBR.emAlta} />
        </TabsContent>
        <TabsContent value="bdrs" className="flex gap-5">
          <HighlightsCard title="Altas" items={mockAcoesBR.emAlta} />
          <HighlightsCard title="Baixas" items={mockAcoesBR.emBaixa} />
          <HighlightsCard
            title="Mais Ativas"
            items={mockAcoesBR.maisNegociados}
          />
          <HighlightsCard title="Dividendos" items={mockAcoesBR.emAlta} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
