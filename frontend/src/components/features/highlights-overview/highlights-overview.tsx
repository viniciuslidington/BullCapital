import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { HighlightsCard } from "./highlights-card";
import { HighlightsDividendCard } from "./highlights-dividend-card";
import { useState, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { QuestionMark } from "@/components/ui/question-mark";
import type { Setores } from "@/types/category";
import { useMultipleCategoryScreenings } from "@/hooks/queries/usecategories";
import {
  Carousel,
  CarouselContent,
  CarouselNext,
} from "@/components/ui/carousel";
import { AlertCircleIcon } from "lucide-react";

export function HighlightsOverview() {
  const [setor, setSetor] = useState<Setores | null>(null);

  const {
    data: response,
    isLoading,
    isFetching,
    isError,
  } = useMultipleCategoryScreenings();

  const navigate = useNavigate();
  const onSeeMore = (filtro: string) =>
    navigate(`/ranking?setor=${setor}&filtro=${filtro}`);

  const fetchState = {
    isLoading,
    isFetching,
    badResponse: (isError || response === undefined) && !isLoading,
  };

  return (
    <div className="flex w-full flex-col gap-2">
      <Tabs
        defaultValue="acoes"
        className="w-full"
        onValueChange={(value) => setSetor(value as Setores)}
      >
        <TabsList className="gap-2 bg-transparent">
          <p className="text-muted-foreground dark:text-foreground mr-2 font-semibold">
            DESTAQUES
          </p>
          <TabsTrigger
            value="acoes"
            className="data-[state=active]:bg-primary data-[state=active]:dark:bg-primary data-[state=active]:text-primary-foreground hover:text-primary dark:hover:text-primary cursor-pointer duration-200"
          >
            Ações
          </TabsTrigger>

          <TabsTrigger
            value="fiis"
            className="data-[state=active]:bg-primary data-[state=active]:dark:bg-primary data-[state=active]:text-primary-foreground hover:text-primary dark:hover:text-primary cursor-pointer duration-200"
          >
            FIIs
          </TabsTrigger>
          <TabsTrigger
            value="etfs"
            className="data-[state=active]:bg-primary data-[state=active]:dark:bg-primary data-[state=active]:text-primary-foreground hover:text-primary dark:hover:text-primary cursor-pointer duration-200"
          >
            ETFs
          </TabsTrigger>
          <TabsTrigger
            value="bdrs"
            className="data-[state=active]:bg-primary data-[state=active]:dark:bg-primary data-[state=active]:text-primary-foreground hover:text-primary dark:hover:text-primary cursor-pointer duration-200"
          >
            BDRs
          </TabsTrigger>
        </TabsList>
      </Tabs>
      <Carousel
        opts={{ dragFree: true }}
        className={`${fetchState.badResponse && "pointer-events-none touch-none"}`}
      >
        <CarouselContent
          className={`-ml-5 select-none ${fetchState.badResponse && "blur-[3px]"}`}
        >
          <HighlightsCard
            title="Altas"
            items={response?.alta_do_dia}
            onSeeMore={() => onSeeMore("altas")}
            fetchState={fetchState}
          />
          <HighlightsCard
            title="Baixas"
            items={response?.baixa_do_dia}
            onSeeMore={() => onSeeMore("baixas")}
            fetchState={fetchState}
          />
          <HighlightsCard
            title="Mais Ativas"
            items={response?.mais_negociadas}
            onSeeMore={() => onSeeMore("ativas")}
            fetchState={fetchState}
          />
          <HighlightsDividendCard
            title="Dividend Yield"
            items={response?.valor_dividendos}
            onSeeMore={() => onSeeMore("dividendos")}
            fetchState={fetchState}
          />
        </CarouselContent>
        <CarouselNext className="disabled:!border-transparent disabled:!bg-transparent disabled:!text-transparent" />
        {fetchState.badResponse && (
          <div className="slide-in-from-top fade-in animate-in bg-card absolute top-1/2 right-1/2 m-auto translate-x-1/2 -translate-y-1/2 rounded-lg border p-3 shadow-lg duration-500">
            <p className="text-destructive flex items-center gap-2 text-sm font-medium">
              <AlertCircleIcon className="h-4 w-4" />
              Falha ao carregar itens
            </p>
          </div>
        )}
      </Carousel>
    </div>
  );
}

function Tooltip({ children, value }: { children: ReactNode; value: Setores }) {
  return (
    <QuestionMark
      dataIndex={value}
      dataType="categoryTitle"
      icon={false}
      side="top"
      delay={600}
    >
      {children}
    </QuestionMark>
  );
}
